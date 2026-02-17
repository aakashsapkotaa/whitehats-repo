from fastapi import APIRouter, HTTPException, Depends, Query
from app.auth import get_current_user
from app.database import (
    groups_collection, group_posts_collection,
    resources_collection, users_collection
)
from app.models import GroupCreate, GroupPostCreate
from app.utils.tokens import award_tokens
from bson import ObjectId
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api", tags=["Groups"])


# --- Create Group ---
@router.post("/groups")
def create_group(body: GroupCreate, current_user: dict = Depends(get_current_user)):
    """Create a new study group."""
    # Check for duplicate name
    if groups_collection.find_one({"name": {"$regex": f"^{body.name}$", "$options": "i"}}):
        raise HTTPException(status_code=400, detail="A group with this name already exists")

    group = {
        "name": body.name,
        "description": body.description,
        "category": body.category,
        "creator_id": current_user["_id"],
        "creator_name": current_user["name"],
        "members": [current_user["_id"]],
        "member_count": 1,
        "created_at": datetime.utcnow(),
    }
    result = groups_collection.insert_one(group)

    # Award tokens for community contribution
    award_tokens(current_user["_id"], "group_create", 5)

    return {"message": "Group created successfully", "id": str(result.inserted_id)}


# --- List Groups ---
@router.get("/groups")
def list_groups(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """List all groups, optionally filtered by search or category."""
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    if category:
        query["category"] = category

    groups = list(
        groups_collection.find(query).sort("created_at", -1).limit(50)
    )
    for g in groups:
        g["_id"] = str(g["_id"])
        g["is_member"] = current_user["_id"] in g.get("members", [])
    return {"groups": groups}


# --- My Groups ---
@router.get("/groups/my")
def my_groups(current_user: dict = Depends(get_current_user)):
    """Get groups the current user belongs to."""
    groups = list(
        groups_collection.find({"members": current_user["_id"]}).sort("created_at", -1)
    )
    for g in groups:
        g["_id"] = str(g["_id"])
        g["is_member"] = True
    return {"groups": groups}


# --- Group Detail ---
@router.get("/groups/{group_id}")
def get_group(group_id: str, current_user: dict = Depends(get_current_user)):
    """Get group detail with recent posts and resources."""
    group = groups_collection.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group["_id"] = str(group["_id"])
    group["is_member"] = current_user["_id"] in group.get("members", [])

    # Recent posts
    posts = list(
        group_posts_collection.find({"group_id": group_id})
        .sort("created_at", -1).limit(30)
    )
    for p in posts:
        p["_id"] = str(p["_id"])

    # Resources shared to this group
    resources = list(
        resources_collection.find({"group_id": group_id})
        .sort("created_at", -1).limit(20)
    )
    for r in resources:
        r["_id"] = str(r["_id"])

    # Member info
    member_ids = group.get("members", [])
    members = []
    for mid in member_ids[:20]:
        user = users_collection.find_one({"_id": ObjectId(mid)}, {"name": 1, "college": 1, "avatar_url": 1})
        if user:
            user["_id"] = str(user["_id"])
            members.append(user)

    return {
        "group": group,
        "posts": posts,
        "resources": resources,
        "members": members,
    }


# --- Join Group ---
@router.post("/groups/{group_id}/join")
def join_group(group_id: str, current_user: dict = Depends(get_current_user)):
    """Join a study group."""
    group = groups_collection.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user["_id"] in group.get("members", []):
        raise HTTPException(status_code=400, detail="You are already a member")

    groups_collection.update_one(
        {"_id": ObjectId(group_id)},
        {"$push": {"members": current_user["_id"]}, "$inc": {"member_count": 1}}
    )
    return {"message": "Joined group successfully"}


# --- Leave Group ---
@router.post("/groups/{group_id}/leave")
def leave_group(group_id: str, current_user: dict = Depends(get_current_user)):
    """Leave a study group."""
    group = groups_collection.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user["_id"] not in group.get("members", []):
        raise HTTPException(status_code=400, detail="You are not a member")

    if group["creator_id"] == current_user["_id"]:
        raise HTTPException(status_code=400, detail="Group creator cannot leave. Delete the group instead.")

    groups_collection.update_one(
        {"_id": ObjectId(group_id)},
        {"$pull": {"members": current_user["_id"]}, "$inc": {"member_count": -1}}
    )
    return {"message": "Left group successfully"}


# --- Post Discussion ---
@router.post("/groups/{group_id}/post")
def post_discussion(group_id: str, body: GroupPostCreate, current_user: dict = Depends(get_current_user)):
    """Post a message in a group discussion."""
    group = groups_collection.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user["_id"] not in group.get("members", []):
        raise HTTPException(status_code=403, detail="You must join the group to post")

    post = {
        "group_id": group_id,
        "user_id": current_user["_id"],
        "user_name": current_user["name"],
        "text": body.text,
        "created_at": datetime.utcnow(),
    }
    group_posts_collection.insert_one(post)
    return {"message": "Posted to group discussion"}


# --- Delete Group (creator only) ---
@router.delete("/groups/{group_id}")
def delete_group(group_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a group (only the creator can do this)."""
    group = groups_collection.find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group["creator_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Only the group creator can delete this group")

    group_posts_collection.delete_many({"group_id": group_id})
    groups_collection.delete_one({"_id": ObjectId(group_id)})
    return {"message": "Group deleted"}
