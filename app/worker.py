from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Upload, Analysis
from .analysis import analyze_image


def process_image(processing_id: str):
    """
    Background worker that processes an uploaded image.
    - Updates upload status
    - Runs image analysis
    - Detects duplicate images
    - Stores results in the analysis table
    """

    print("=" * 50)
    print("WORKER STARTED")
    print("Processing ID:", processing_id)
    print("=" * 50)

    db: Session = SessionLocal()

    try:
        # Fetch uploaded image record
        upload = db.query(Upload).filter(Upload.id == processing_id).first()

        if not upload:
            print("Upload record not found")
            return

        print("File path:", upload.filepath)

        # Update status -> processing
        upload.status = "processing"
        db.commit()

        # Run OpenCV + OCR analysis
        result = analyze_image(upload.filepath)

        print("Analysis result:")
        print(result)

        # Duplicate detection using image hash
        duplicate = False

        existing_hashes = db.query(Analysis).all()

        for row in existing_hashes:
            if row.image_hash == result["image_hash"]:
                duplicate = True
                print("Duplicate image detected")
                break

        # Save analysis
        analysis = Analysis(
            upload_id=processing_id,
            blur_score=result["blur_score"],
            is_blurry=result["is_blurry"],
            brightness=result["brightness"],
            low_light=result["low_light"],
            duplicate=duplicate,
            image_hash=result["image_hash"],
            ocr_text=result["ocr_text"],
            number_plate_valid=result["number_plate_valid"],
            screenshot_suspected=result["screenshot_suspected"],
        )

        db.add(analysis)

        # Mark upload completed
        upload.status = "completed"

        db.commit()

        print("Analysis inserted successfully")
        print("Upload marked as completed")

    except Exception as e:
        print("BACKGROUND ERROR:", repr(e))

        # Mark upload as failed
        upload = db.query(Upload).filter(Upload.id == processing_id).first()

        if upload:
            upload.status = "failed"
            upload.failure_reason = str(e)
            db.commit()

    finally:
        db.close()
        print("Worker finished")
        print("=" * 50)