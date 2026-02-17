from fastapi import APIRouter, HTTPException, Depends
from app.database import reviews_collection, resources_collection
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Reviews"])


@router.post("/resources/{resource_id}/reviews")
def add_or_update_review(resource_id: str, rating: int, comment: str = "",
                         current_user: dict = Depends(get_current_user)):
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Check access for private resource
    if resource["privacy"] == "private" and resource.get("college") != current_user.get("college", ""):
        raise HTTPException(status_code=403, detail="Access denied")

    existing = reviews_collection.find_one({
        "resource_id": resource_id,
        "user_id": current_user["_id"]
    })

    if existing:
        # Update existing review
        reviews_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {"rating": rating, "comment": comment, "updated_at": datetime.utcnow()}}
        )
        msg = "Review updated"
    else:
        # Create new review
        reviews_collection.insert_one({
            "resource_id": resource_id,
            "user_id": current_user["_id"],
            "user_name": current_user["name"],
            "rating": rating,
            "comment": comment,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        msg = "Review added"

    # Recalculate average
    pipeline = [
        {"$match": {"resource_id": resource_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    result = list(reviews_collection.aggregate(pipeline))
    if result:
        avg_rating = round(result[0]["avg"], 1)
        total = result[0]["count"]
    else:
        avg_rating = 0
        total = 0

    resources_collection.update_one(
        {"_id": ObjectId(resource_id)},
        {"$set": {"avg_rating": avg_rating, "total_reviews": total}}
    )

    return {"message": msg, "avg_rating": avg_rating, "total_reviews": total}


@router.get("/resources/{resource_id}/reviews")
def get_reviews(resource_id: str):
    reviews = list(reviews_collection.find({"resource_id": resource_id}).sort("created_at", -1))
    for r in reviews:
        r["_id"] = str(r["_id"])
    return {"reviews": reviews}
