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
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Indian number plate pattern
INDIAN_PLATE_REGEX = r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}"


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
# Image Hash
# --------------------------------------------------
def compute_hash(filepath):
    return str(imagehash.phash(Image.open(filepath)))


# --------------------------------------------------
# OCR Text Extraction
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

        # Enlarge image for better OCR
        gray = cv2.resize(
            gray,
            None,
            fx=2.5,
            fy=2.5,
            interpolation=cv2.INTER_CUBIC
        )

        # Sharpen image
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])
        gray = cv2.filter2D(gray, -1, kernel)

        # Threshold
        thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        # OCR configuration
        config = (
            "--oem 3 --psm 6 "
            "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )

        text = pytesseract.image_to_string(thresh, config=config)

        # Clean OCR output
        text = text.upper()
        text = re.sub(r"[^A-Z0-9]", "", text)

        return text

    except Exception as e:
        print("OCR Error:", e)
        return ""


# --------------------------------------------------
# Number Plate Validation
# --------------------------------------------------
def validate_indian_number_plate(text):
    if not text:
        return None

    cleaned = text.upper().replace(" ", "").replace("\n", "")
    match = re.search(INDIAN_PLATE_REGEX, cleaned)

    return match.group(0) if match else None


# --------------------------------------------------
# Screenshot Detection
# --------------------------------------------------
def detect_screenshot(image):
    h, w = image.shape[:2]

    ratio = w / h

    phone_like = 0.45 < ratio < 0.65

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    edge_density = edges.mean()

    return phone_like and edge_density < 15


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
        "ocr_text": text if text else "",
        "number_plate_valid": plate is not None,
        "screenshot_suspected": screenshot,
    }