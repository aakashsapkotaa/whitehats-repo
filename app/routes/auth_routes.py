from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.database import users_collection
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models import UserRegister, UserLogin
from datetime import datetime
import os, uuid

router = APIRouter(prefix="/api", tags=["Auth"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


@router.post("/register")
def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "college": user.college,
        "branch": user.branch,
        "semester": user.semester,
        "avatar_url": "",
        "created_at": datetime.utcnow(),
    }
    result = users_collection.insert_one(new_user)
    token = create_access_token({"user_id": str(result.inserted_id)})
    return {"message": "Registration successful", "token": token, "user": {"name": user.name, "email": user.email}}


@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"user_id": str(db_user["_id"])})
    return {
        "message": "Login successful",
        "token": token,
        "user": {"name": db_user["name"], "email": db_user["email"], "college": db_user["college"]},
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
    users_collection.update_one({"_id": __import__("bson").ObjectId(current_user["_id"])}, {"$set": {"avatar_url": avatar_url}})
    return {"message": "Avatar uploaded", "avatar_url": avatar_url}
