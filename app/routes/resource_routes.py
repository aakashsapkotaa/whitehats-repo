from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from app.database import resources_collection, reviews_collection, scan_logs_collection
from app.auth import get_current_user
from app.utils.scanner import compute_sha256, scan_upload, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.utils.tokens import award_tokens
from bson import ObjectId
from datetime import datetime
from typing import Optional
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
    tags: str = Form(""),
    privacy: str = Form("public"),
    group_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
):
    # Read file content
    content = await file.read()

    # 1. File size check
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE // (1024*1024)}MB")

    # 2. Extension check
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed")

    # 3. SHA256 duplicate check
    file_hash = compute_sha256(content)
    existing = resources_collection.find_one({"file_hash": file_hash})
    if existing:
        raise HTTPException(status_code=409, detail="Duplicate file detected. This file has already been uploaded.")

    # 4. Malware scan
    is_clean, scan_msg = scan_upload(content, file.filename)

    # Log scan result
    scan_logs_collection.insert_one({
        "filename": file.filename,
        "file_hash": file_hash,
        "is_clean": is_clean,
        "message": scan_msg,
        "uploader_id": current_user["_id"],
        "uploader_name": current_user["name"],
        "scanned_at": datetime.utcnow(),
    })

    if not is_clean:
        # Reward for reporting malware (the scan caught it)
        award_tokens(current_user["_id"], "malware_report")
        raise HTTPException(status_code=400, detail=f"File rejected: {scan_msg}")

    # 5. Save file
    safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(filepath, "wb") as f:
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
        "file_hash": file_hash,
        "file_size": len(content),
        "scan_status": "clean",
        "scan_result": scan_msg,
        "uploader_id": current_user["_id"],
        "uploader_name": current_user["name"],
        "college": current_user.get("college", ""),
        "created_at": datetime.utcnow(),
        "avg_rating": 0,
        "total_reviews": 0,
        "likes_count": 0,
        "group_id": group_id if group_id else None,
    }
    result = resources_collection.insert_one(resource)

    # Reward safe upload tokens
    award_tokens(current_user["_id"], "safe_upload")

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

    if not privacy:
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

    if resource["privacy"] == "private" and resource.get("college") != current_user.get("college", ""):
        raise HTTPException(status_code=403, detail="Access denied. This resource is private to another college.")

    # Award explore view token
    award_tokens(current_user["_id"], "explore_view")

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

    filepath = os.path.join(UPLOAD_DIR, resource["file_path"])
    if os.path.exists(filepath):
        os.remove(filepath)

    reviews_collection.delete_many({"resource_id": resource_id})
    resources_collection.delete_one({"_id": ObjectId(resource_id)})
    return {"message": "Resource deleted"}


@router.get("/resources/{resource_id}/download")
def download_resource(resource_id: str, current_user: dict = Depends(get_current_user)):
    resource = resources_collection.find_one({"_id": ObjectId(resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if resource["privacy"] == "private" and resource.get("college") != current_user.get("college", ""):
        raise HTTPException(status_code=403, detail="Access denied")

    filepath = os.path.join(UPLOAD_DIR, resource["file_path"])
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(filepath, filename=resource["file_name"], media_type="application/octet-stream")
