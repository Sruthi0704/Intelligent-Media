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

# Indian number plate format (e.g., KA01AB1234)
INDIAN_PLATE_REGEX = r"\b[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}\b"


# --------------------------------------------------
# Blur Detection
# --------------------------------------------------
def detect_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance, variance < 100


# --------------------------------------------------
# Brightness Analysis
# --------------------------------------------------
def analyze_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    return brightness, brightness < 80


# --------------------------------------------------
# Image Hash (Duplicate Detection)
# --------------------------------------------------
def compute_hash(filepath):
    return str(imagehash.phash(Image.open(filepath)))


# --------------------------------------------------
# OCR Text Extraction (Improved)
# --------------------------------------------------
def extract_text(filepath):
    try:
        image = cv2.imread(filepath)

        if image is None:
            return ""

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Improve contrast
        gray = cv2.equalizeHist(gray)

        # Resize image (2x) for better OCR accuracy
        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        # Reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Thresholding
        thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        # OCR configuration optimized for license plates
        config = "--oem 3 --psm 7"

        text = pytesseract.image_to_string(thresh, config=config)

        return text.strip()

    except Exception as e:
        print("OCR Error:", e)
        return ""


# --------------------------------------------------
# Indian Number Plate Validation
# --------------------------------------------------
def validate_indian_number_plate(text):
    cleaned = text.upper().replace(" ", "").replace("\n", "")
    match = re.search(INDIAN_PLATE_REGEX, cleaned)
    return match.group(0) if match else None


# --------------------------------------------------
# Screenshot Detection
# --------------------------------------------------
def detect_screenshot(image):
    height, width = image.shape[:2]
    aspect_ratio = width / height

    # Common mobile screenshot aspect ratios
    common_ratios = [9 / 16, 10 / 16, 9 / 19.5, 9 / 20]

    score = min(abs(aspect_ratio - r) for r in common_ratios)

    return score < 0.05


# --------------------------------------------------
# Complete Image Analysis
# --------------------------------------------------
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
        "blur_score": round(float(blur_score), 2),
        "is_blurry": blurry,
        "brightness": round(float(brightness), 2),
        "low_light": low_light,
        "image_hash": img_hash,
        "ocr_text": text,
        "number_plate_valid": plate is not None,
        "screenshot_suspected": screenshot,
    }