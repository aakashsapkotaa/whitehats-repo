"""
EduToken reward system — central helper for awarding and querying tokens.
"""
from datetime import datetime
from bson import ObjectId
from app.database import users_collection, token_logs_collection

# Reward amounts
REWARDS = {
    "safe_upload": 10,
    "malware_report": 15,
    "daily_login": 5,
    "ocr_usage": 2,
    "high_rated_file": 5,
    "explore_view": 1,
}


def award_tokens(user_id: str, reason: str, amount: int | None = None):
    """Award EduTokens to a user and log the transaction."""
    if amount is None:
        amount = REWARDS.get(reason, 0)
    if amount <= 0:
        return

    # Update user token balance
    update = {"$inc": {"edutokens": amount}}
    if reason == "explore_view":
        update["$inc"]["explore_score"] = 1

    users_collection.update_one({"_id": ObjectId(user_id)}, update)

    # Log transaction
    token_logs_collection.insert_one({
        "user_id": user_id,
        "reason": reason,
        "amount": amount,
        "created_at": datetime.utcnow(),
    })


def get_user_tokens(user_id: str) -> dict:
    """Get token balance and explore score for a user."""
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {
        "edutokens": 1, "explore_score": 1, "name": 1
    })
    if not user:
        return {"edutokens": 0, "explore_score": 0}
    return {
        "edutokens": user.get("edutokens", 0),
        "explore_score": user.get("explore_score", 0),
    }
