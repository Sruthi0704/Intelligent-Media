from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(String(36), primary_key=True, index=True)
    filename = Column(String(255))
    filepath = Column(String(500))
    status = Column(String(20), default="pending")
    failure_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship(
        "Analysis",
        back_populates="upload",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Analysis(Base):
    __tablename__ = "analysis"

    upload_id = Column(String(36), ForeignKey("uploads.id"), primary_key=True)

    blur_score = Column(Float)
    is_blurry = Column(Boolean)

    brightness = Column(Float)
    low_light = Column(Boolean)

    duplicate = Column(Boolean)
    image_hash = Column(String(64))

    ocr_text = Column(String(500))
    number_plate_valid = Column(Boolean)

    screenshot_suspected = Column(Boolean)

    upload = relationship("Upload", back_populates="analysis")