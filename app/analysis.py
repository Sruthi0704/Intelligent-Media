import os
import re
import cv2
import numpy as np
import pytesseract
import imagehash
from PIL import Image

# --------------------------------------------------
# Configure Tesseract for Windows and Render/Linux
# --------------------------------------------------
if os.name == "nt":
    # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    # Linux / Render
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

INDIAN_PLATE_REGEX = r"\b[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}\b"


def detect_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance, variance < 100


def analyze_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    return brightness, brightness < 80


def compute_hash(filepath):
    return str(imagehash.phash(Image.open(filepath)))


def extract_text(filepath):
    try:
        text = pytesseract.image_to_string(Image.open(filepath))
        return text.strip()
    except Exception:
        return ""


def validate_indian_number_plate(text):
    cleaned = text.upper().replace(" ", "").replace("\n", "")
    match = re.search(INDIAN_PLATE_REGEX, cleaned)
    return match.group(0) if match else None


def detect_screenshot(image):
    height, width = image.shape[:2]
    aspect_ratio = width / height
    common_ratios = [9/16, 10/16, 9/19.5, 9/20]
    score = min(abs(aspect_ratio - r) for r in common_ratios)
    return score < 0.05


def analyze_image(filepath):
    image = cv2.imread(filepath)

    if image is None:
        raise ValueError("Could not read image")

    blur_score, blurry = detect_blur(image)
    brightness, low_light = analyze_brightness(image)
    img_hash = compute_hash(filepath)
    text = extract_text(filepath)
    plate = validate_indian_number_plate(text)
    screenshot = detect_screenshot(image)

    return {
        "blur_score": blur_score,
        "is_blurry": blurry,
        "brightness": brightness,
        "low_light": low_light,
        "image_hash": img_hash,
        "ocr_text": text,
        "number_plate_valid": plate is not None,
        "screenshot_suspected": screenshot,
    }