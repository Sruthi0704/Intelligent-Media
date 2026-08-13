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
INDIAN_PLATE_REGEX = r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}"

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

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Improve contrast
        gray = cv2.equalizeHist(gray)

        # Detect edges
        edged = cv2.Canny(gray, 100, 200)

        # Find contours
        contours, _ = cv2.findContours(
            edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

        plate_region = None

        # Look for a rectangular region that resembles a license plate
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)

                if 2.0 < aspect_ratio < 6.5 and w > 80 and h > 20:
                    plate_region = gray[y:y+h, x:x+w]
                    break

        # If no plate detected, use entire image
        if plate_region is None:
            plate_region = gray

        # Enlarge the region
        plate_region = cv2.resize(
            plate_region,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_CUBIC
        )

        # Threshold for better OCR
        plate_region = cv2.threshold(
            plate_region,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        config = (
            "--oem 3 --psm 7 "
            "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )

        text = pytesseract.image_to_string(plate_region, config=config)

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