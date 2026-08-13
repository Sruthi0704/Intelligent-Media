import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from .database import get_db
from .models import Upload, Analysis
from .worker import process_image

router = APIRouter()

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate image type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    processing_id = str(uuid.uuid4())

    extension = os.path.splitext(file.filename)[1]
    filename = f"{processing_id}{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save image locally
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    # Store metadata in MySQL
    upload = Upload(
        id=processing_id,
        filename=file.filename,
        filepath=filepath,
        status="pending",
    )

    db.add(upload)
    db.commit()

    # Start asynchronous processing
    background_tasks.add_task(process_image, processing_id)

    return {
        "processing_id": processing_id,
        "status": "pending",
    }


# ----------------------------
# Get processing status
# ----------------------------
@router.get("/status/{processing_id}")
def get_status(processing_id: str, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == processing_id).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Processing ID not found")

    return {
        "processing_id": processing_id,
        "status": upload.status,
    }


# ----------------------------
# Get analysis result
# ----------------------------
@router.get("/result/{processing_id}")
def get_result(processing_id: str, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == processing_id).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Processing ID not found")

    analysis = db.query(Analysis).filter(
        Analysis.upload_id == processing_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "processing_id": processing_id,
        "status": upload.status,
        "analysis": {
            "blur_score": analysis.blur_score,
            "is_blurry": analysis.is_blurry,
            "brightness": analysis.brightness,
            "low_light": analysis.low_light,
            "duplicate": analysis.duplicate,
            "ocr_text": analysis.ocr_text,
            "number_plate_valid": analysis.number_plate_valid,
            "screenshot_suspected": analysis.screenshot_suspected,
        },
    }


# ----------------------------
# Get failure reason
# ----------------------------
@router.get("/failure/{processing_id}")
def get_failure(processing_id: str, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == processing_id).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Processing ID not found")

    return {
        "processing_id": processing_id,
        "status": upload.status,
        "failure_reason": upload.failure_reason,
    }
    