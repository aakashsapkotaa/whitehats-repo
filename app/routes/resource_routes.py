from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from app.database import resources_collection, reviews_collection
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime
from typing import Optional, List
import os, uuid

router = APIRouter(prefix="/api", tags=["Resources"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


@router.post("/resources")
async def create_resource(
    file: UploadFile = File(...),
    title: str = Form(...),
    subject: str = Form(...),
    semester: int = Form(...),
    resource_type: str = Form(...),
    year: Optional[int] = Form(None),
    description: str = Form(""),
    tags: str = Form(""),  # comma-separated
    privacy: str = Form("public"),
    current_user: dict = Depends(get_current_user),
):
    # Save file
    ext = os.path.splitext(file.filename)[1]
    safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    resource = {
        "title": title,
        "subject": subject,
        "semester": semester,
        "resource_type": resource_type,
        "year": year,
        "description": description,
        "tags": tag_list,
        "privacy": privacy.lower(),
        "file_name": file.filename,
        "file_path": safe_name,
        "uploader_id": current_user["_id"],
        "uploader_name": current_user["name"],
        "college": current_user.get("college", ""),
        "created_at": datetime.utcnow(),
        "avg_rating": 0,
        "total_reviews": 0,
    }
    result = resources_collection.insert_one(resource)
    return {"message": "Resource uploaded successfully", "id": str(result.inserted_id)}


@router.get("/resources")
def list_resources(
    search: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    privacy: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    query = {}

    # Search by title, subject, or tags
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"subject": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
        ]

    if semester:
        query["semester"] = semester
    if resource_type:
        query["resource_type"] = resource_type
    if privacy:
        query["privacy"] = privacy.lower()

    # Access control: always hide private resources from other colleges
    if not privacy:
        # No privacy filter set — show public + same-college private
        access_filter = {
            "$or": [
                {"privacy": "public"},
                {"privacy": "private", "college": current_user.get("college", "")},
            ]
        }
        if "$and" not in query:
            query["$and"] = []
        query["$and"].append(access_filter)
    elif privacy == "private":
        # Explicitly filtering private — only show same-college
        query["college"] = current_user.get("college", "")

    skip = (page - 1) * limit
    cursor = resources_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)

    resources = []
    for r in cursor:
        r["_id"] = str(r["_id"])
        resources.append(r)

    total = resources_collection.count_documents(query)
    return {"resources": resources, "total": total, "page": page, "pages": (total + limit - 1) // limit}


@router.get("/resources/{resource_id}")
def get_resource(resource_id: str, current_user: dict = Depends(get_current_user)):
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Access control for private resources
    if resource["privacy"] == "private" and resource["college"] != current_user.get("college", ""):
        raise HTTPException(status_code=403, detail="Access denied. This resource is private to another college.")

    resource["_id"] = str(resource["_id"])
    return resource


@router.put("/resources/{resource_id}")
def update_resource(resource_id: str, title: str = Form(None), subject: str = Form(None),
                    semester: int = Form(None), resource_type: str = Form(None),
                    year: int = Form(None), description: str = Form(None),
                    tags: str = Form(None), privacy: str = Form(None),
                    current_user: dict = Depends(get_current_user)):
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource["uploader_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="You can only edit your own resources")

    updates = {}
    if title is not None: updates["title"] = title
    if subject is not None: updates["subject"] = subject
    if semester is not None: updates["semester"] = semester
    if resource_type is not None: updates["resource_type"] = resource_type
    if year is not None: updates["year"] = year
    if description is not None: updates["description"] = description
    if tags is not None: updates["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    if privacy is not None: updates["privacy"] = privacy.lower()

    if updates:
        resources_collection.update_one({"_id": ObjectId(resource_id)}, {"$set": updates})
    return {"message": "Resource updated"}


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: str, current_user: dict = Depends(get_current_user)):
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource["uploader_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="You can only delete your own resources")

    # Delete file
    filepath = os.path.join(UPLOAD_DIR, resource["file_path"])
    if os.path.exists(filepath):
        os.remove(filepath)

    # Delete reviews
    reviews_collection.delete_many({"resource_id": resource_id})
    resources_collection.delete_one({"_id": ObjectId(resource_id)})
    return {"message": "Resource deleted"}


@router.get("/resources/{resource_id}/download")
def download_resource(resource_id: str, current_user: dict = Depends(get_current_user)):
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if resource["privacy"] == "private" and resource["college"] != current_user.get("college", ""):
        raise HTTPException(status_code=403, detail="Access denied")

    filepath = os.path.join(UPLOAD_DIR, resource["file_path"])
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(filepath, filename=resource["file_name"], media_type="application/octet-stream")
