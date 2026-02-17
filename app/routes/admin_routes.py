from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_admin_user
from app.database import (
    reports_collection, scan_logs_collection,
    users_collection, resources_collection
)
from bson import ObjectId

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/flagged")
def flagged_files(admin: dict = Depends(get_admin_user)):
    """View all reported/flagged files."""
    reports = list(reports_collection.find().sort("created_at", -1).limit(50))
    for r in reports:
        r["_id"] = str(r["_id"])
    return {"reports": reports}


@router.get("/malicious")
def malicious_uploads(admin: dict = Depends(get_admin_user)):
    """View scan logs where files were flagged as malicious."""
    logs = list(
        scan_logs_collection.find({"is_clean": False})
        .sort("scanned_at", -1)
        .limit(50)
    )
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"malicious_logs": logs}


@router.post("/ban/{user_id}")
def ban_user(user_id: str, admin: dict = Depends(get_admin_user)):
    """Ban a user."""
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Cannot ban an admin")

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_banned": True}}
    )
    return {"message": f"User {user.get('name', user_id)} has been banned"}


@router.post("/unban/{user_id}")
def unban_user(user_id: str, admin: dict = Depends(get_admin_user)):
    """Unban a user."""
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_banned": False}}
    )
    return {"message": f"User {user.get('name', user_id)} has been unbanned"}


@router.delete("/resources/{resource_id}")
def admin_delete_resource(resource_id: str, admin: dict = Depends(get_admin_user)):
    """Admin force-delete a resource."""
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    import os
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    filepath = os.path.join(UPLOAD_DIR, resource.get("file_path", ""))
    if os.path.exists(filepath):
        os.remove(filepath)

    resources_collection.delete_one({"_id": ObjectId(resource_id)})
    # Clean up reports for this resource
    reports_collection.delete_many({"resource_id": resource_id})
    return {"message": "Resource deleted by admin"}


@router.get("/users")
def list_users(admin: dict = Depends(get_admin_user)):
    """List all users (for admin panel)."""
    users = list(
        users_collection.find(
            {},
            {"password": 0}
        ).sort("created_at", -1).limit(100)
    )
    for u in users:
        u["_id"] = str(u["_id"])
    return {"users": users}
