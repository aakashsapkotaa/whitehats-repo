from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_current_user
from app.database import (
    resources_collection, comments_collection, likes_collection,
    reports_collection, users_collection
)
from app.models import CommentCreate, ReportCreate
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Community"])


# --- Likes / Upvotes ---
@router.post("/resources/{resource_id}/like")
def toggle_like(resource_id: str, current_user: dict = Depends(get_current_user)):
    """Toggle like on a resource. Like again to unlike."""
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    existing = likes_collection.find_one({
        "resource_id": resource_id,
        "user_id": current_user["_id"]
    })

    if existing:
        # Unlike
        likes_collection.delete_one({"_id": existing["_id"]})
        resources_collection.update_one(
            {"_id": ObjectId(resource_id)},
            {"$inc": {"likes_count": -1}}
        )
        return {"liked": False, "likes_count": max(0, resource.get("likes_count", 1) - 1)}
    else:
        # Like
        likes_collection.insert_one({
            "resource_id": resource_id,
            "user_id": current_user["_id"],
            "created_at": datetime.utcnow(),
        })
        resources_collection.update_one(
            {"_id": ObjectId(resource_id)},
            {"$inc": {"likes_count": 1}}
        )
        new_count = resource.get("likes_count", 0) + 1
        return {"liked": True, "likes_count": new_count}


@router.get("/resources/{resource_id}/likes")
def get_likes(resource_id: str, current_user: dict = Depends(get_current_user)):
    """Get like count and whether current user liked it."""
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    user_liked = likes_collection.find_one({
        "resource_id": resource_id,
        "user_id": current_user["_id"]
    }) is not None

    return {
        "likes_count": resource.get("likes_count", 0),
        "user_liked": user_liked,
    }


# --- Comments ---
@router.post("/resources/{resource_id}/comments")
def add_comment(resource_id: str, body: CommentCreate, current_user: dict = Depends(get_current_user)):
    """Add a comment to a resource."""
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    comment = {
        "resource_id": resource_id,
        "user_id": current_user["_id"],
        "user_name": current_user["name"],
        "text": body.text,
        "created_at": datetime.utcnow(),
    }
    comments_collection.insert_one(comment)
    return {"message": "Comment added"}


@router.get("/resources/{resource_id}/comments")
def get_comments(resource_id: str):
    """Get all comments for a resource."""
    comments = list(
        comments_collection.find({"resource_id": resource_id})
        .sort("created_at", -1)
        .limit(100)
    )
    for c in comments:
        c["_id"] = str(c["_id"])
    return {"comments": comments}


# --- Reports ---
@router.post("/resources/{resource_id}/report")
def report_resource(resource_id: str, body: ReportCreate, current_user: dict = Depends(get_current_user)):
    """Report a resource for review."""
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Prevent duplicate reports
    existing = reports_collection.find_one({
        "resource_id": resource_id,
        "reporter_id": current_user["_id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already reported this resource")

    reports_collection.insert_one({
        "resource_id": resource_id,
        "resource_title": resource.get("title", ""),
        "reporter_id": current_user["_id"],
        "reporter_name": current_user["name"],
        "reason": body.reason,
        "created_at": datetime.utcnow(),
    })
    return {"message": "Report submitted. Thank you for keeping the community safe."}


# --- Community Trust Score ---
@router.get("/community/trust/{user_id}")
def trust_score(user_id: str, current_user: dict = Depends(get_current_user)):
    """Calculate community trust score for a user."""
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Count uploads
    total_uploads = resources_collection.count_documents({"uploader_id": user_id})

    # Average rating of their uploads
    pipeline = [
        {"$match": {"uploader_id": user_id, "avg_rating": {"$gt": 0}}},
        {"$group": {"_id": None, "avg": {"$avg": "$avg_rating"}}}
    ]
    avg_result = list(resources_collection.aggregate(pipeline))
    avg_rating = round(avg_result[0]["avg"], 1) if avg_result else 0

    # Reports against this user's resources
    user_resources = [str(r["_id"]) for r in resources_collection.find({"uploader_id": user_id}, {"_id": 1})]
    reports_against = reports_collection.count_documents({"resource_id": {"$in": user_resources}}) if user_resources else 0

    # Trust = uploads * 2 + avg_rating * 10 - reports * 5 (min 0)
    score = max(0, (total_uploads * 2) + (avg_rating * 10) - (reports_against * 5))

    return {
        "user_id": user_id,
        "name": user.get("name", ""),
        "trust_score": round(score, 1),
        "total_uploads": total_uploads,
        "avg_rating": avg_rating,
        "reports_against": reports_against,
    }
