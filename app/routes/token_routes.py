from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import users_collection, token_logs_collection
from app.utils.tokens import get_user_tokens

router = APIRouter(prefix="/api", tags=["Tokens"])


@router.get("/tokens/me")
def my_tokens(current_user: dict = Depends(get_current_user)):
    """Get current user's EduToken balance and explore score."""
    info = get_user_tokens(current_user["_id"])
    return {
        "edutokens": info["edutokens"],
        "explore_score": info["explore_score"],
        "name": current_user["name"],
    }


@router.get("/tokens/history")
def token_history(current_user: dict = Depends(get_current_user)):
    """Get token transaction history for the current user."""
    logs = list(
        token_logs_collection.find({"user_id": current_user["_id"]})
        .sort("created_at", -1)
        .limit(50)
    )
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"history": logs}


@router.get("/leaderboard")
def leaderboard(current_user: dict = Depends(get_current_user)):
    """Top 20 users by EduTokens."""
    top_users = list(
        users_collection.find(
            {"is_banned": {"$ne": True}},
            {"name": 1, "college": 1, "edutokens": 1, "explore_score": 1, "avatar_url": 1}
        )
        .sort("edutokens", -1)
        .limit(20)
    )
    result = []
    for i, u in enumerate(top_users, 1):
        result.append({
            "rank": i,
            "name": u.get("name", "Unknown"),
            "college": u.get("college", ""),
            "edutokens": u.get("edutokens", 0),
            "explore_score": u.get("explore_score", 0),
            "avatar_url": u.get("avatar_url", ""),
        })
    return {"leaderboard": result}
