from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.database import users_collection
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models import UserRegister, UserLogin
from app.utils.otp import generate_otp, send_otp_email, store_otp, verify_otp
from datetime import datetime
from pydantic import BaseModel
import os, uuid

router = APIRouter(prefix="/api", tags=["Auth"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


# --- OTP Models ---
class OTPVerify(BaseModel):
    email: str
    otp: str


class OTPResend(BaseModel):
    email: str


# --- Step 1: Register → Send OTP ---
@router.post("/register")
def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate and send OTP
    otp = generate_otp()
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "college": user.college,
        "branch": user.branch,
        "semester": user.semester,
    }
    store_otp(user.email, otp, user_data)

    sent = send_otp_email(user.email, otp)
    if not sent:
        # For development: allow bypass if email fails
        print(f"[AUTH] Email failed but allowing bypass. OTP for {user.email}: {otp}")
        return {"message": "OTP sent to your email (dev mode - check console)", "email": user.email, "otp_required": True}

    return {"message": "OTP sent to your email", "email": user.email, "otp_required": True}


# --- Step 2: Verify OTP → Create Account ---
@router.post("/verify-otp")
def verify_otp_endpoint(body: OTPVerify):
    user_data = verify_otp(body.email, body.otp)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP. Please try again.")

    # Check email again (race condition safety)
    if users_collection.find_one({"email": user_data["email"]}):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = {
        "name": user_data["name"],
        "email": user_data["email"],
        "password": user_data["password"],
        "college": user_data["college"],
        "branch": user_data["branch"],
        "semester": user_data["semester"],
        "avatar_url": "",
        "edutokens": 0,
        "explore_score": 0,
        "role": "user",
        "is_banned": False,
        "email_verified": True,
        "last_login_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "created_at": datetime.utcnow(),
    }
    result = users_collection.insert_one(new_user)
    token = create_access_token({"user_id": str(result.inserted_id)})
    return {
        "message": "Email verified! Account created successfully",
        "token": token,
        "user": {"name": user_data["name"], "email": user_data["email"]},
    }


# --- Resend OTP ---
@router.post("/resend-otp")
def resend_otp(body: OTPResend):
    from app.utils.otp import otp_store
    entry = otp_store.get(body.email)
    if not entry:
        raise HTTPException(status_code=400, detail="No pending registration for this email. Please register again.")

    otp = generate_otp()
    entry["otp"] = otp
    entry["attempts"] = 0
    from datetime import timedelta
    entry["expires_at"] = datetime.utcnow() + timedelta(minutes=5)

    sent = send_otp_email(body.email, otp)
    if not sent:
        raise HTTPException(status_code=500, detail="Failed to resend OTP")

    return {"message": "New OTP sent to your email"}


@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if db_user.get("is_banned", False):
        raise HTTPException(status_code=403, detail="Your account has been banned")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Update last login date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    users_collection.update_one(
        {"_id": db_user["_id"]},
        {"$set": {"last_login_date": today}}
    )

    token = create_access_token({"user_id": str(db_user["_id"])})
    return {
        "message": "Login successful",
        "token": token,
        "user": {"name": db_user["name"], "email": db_user["email"], "college": db_user.get("college", "")},
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    ext = os.path.splitext(file.filename)[1]
    filename = f"avatar_{current_user['_id']}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    avatar_url = f"/uploads/{filename}"
    from bson import ObjectId
    users_collection.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": {"avatar_url": avatar_url}})
    return {"message": "Avatar uploaded", "avatar_url": avatar_url}
