from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.auth import get_current_user
from app.database import ocr_results_collection
from app.utils.tokens import award_tokens
from datetime import datetime
import os, io

router = APIRouter(prefix="/api", tags=["OCR"])

# --- Check available OCR backends ---
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
except Exception:
    pass

ALLOWED_OCR_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".pdf"}

# --- OCR.space free API (fallback) ---
OCR_SPACE_API_KEY = "helloworld"  # Free tier key from OCR.space


async def ocr_with_tesseract(content: bytes, filename: str) -> str:
    """Extract text using local Tesseract installation."""
    from PIL import Image
    import pytesseract
    image = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(image).strip()


async def ocr_with_api(content: bytes, filename: str) -> str:
    """Extract text using OCR.space free API (supports images + PDF)."""
    import httpx

    ext = os.path.splitext(filename)[1].lower()
    is_pdf = ext == ".pdf"

    url = "https://api.ocr.space/parse/image"

    async with httpx.AsyncClient(timeout=60) as client:
        files = {"file": (filename, content, "application/pdf" if is_pdf else "image/png")}
        data = {
            "apikey": OCR_SPACE_API_KEY,
            "language": "eng",
            "isOverlayRequired": "false",
            "filetype": "PDF" if is_pdf else ext.replace(".", "").upper(),
            "scale": "true",
            "OCREngine": "2",
        }

        response = await client.post(url, files=files, data=data)

    if response.status_code != 200:
        raise Exception(f"OCR API returned status {response.status_code}")

    result = response.json()

    if result.get("IsErroredOnProcessing", False):
        error_msg = result.get("ErrorMessage", ["Unknown error"])
        raise Exception(f"OCR API error: {error_msg}")

    parsed_results = result.get("ParsedResults", [])
    if not parsed_results:
        raise Exception("No text could be extracted")

    # Combine text from all pages
    text = "\n".join(pr.get("ParsedText", "") for pr in parsed_results).strip()
    return text


@router.post("/ocr/extract")
async def extract_text(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload an image or PDF and extract text using OCR."""

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_OCR_EXTS:
        raise HTTPException(status_code=400, detail=f"Only image/PDF files allowed. Got: {ext}")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    extracted_text = ""
    method_used = ""

    # Strategy 1: Use Tesseract if available (images only)
    if TESSERACT_AVAILABLE and ext != ".pdf":
        try:
            extracted_text = await ocr_with_tesseract(content, file.filename)
            method_used = "tesseract"
        except Exception:
            pass  # Fall through to API

    # Strategy 2: Use OCR.space API (images + PDF)
    if not extracted_text:
        try:
            extracted_text = await ocr_with_api(content, file.filename)
            method_used = "ocr_api"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    if not extracted_text:
        extracted_text = "(No text detected in this file)"

    # Save result
    result = ocr_results_collection.insert_one({
        "user_id": current_user["_id"],
        "user_name": current_user["name"],
        "filename": file.filename,
        "extracted_text": extracted_text,
        "method": method_used,
        "created_at": datetime.utcnow(),
    })

    # Award tokens
    award_tokens(current_user["_id"], "ocr_usage")

    return {
        "message": "Text extracted successfully",
        "text": extracted_text,
        "id": str(result.inserted_id),
        "method": method_used,
    }


@router.get("/ocr/history")
def ocr_history(current_user: dict = Depends(get_current_user)):
    """Get OCR history for current user."""
    results = list(
        ocr_results_collection.find({"user_id": current_user["_id"]})
        .sort("created_at", -1)
        .limit(20)
    )
    for r in results:
        r["_id"] = str(r["_id"])
    return {"results": results}
