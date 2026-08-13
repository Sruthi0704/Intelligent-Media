# Intelligent Media Processing Pipeline

## Overview

The Intelligent Media Processing Pipeline is a full-stack web application that analyzes uploaded vehicle images and generates quality and authenticity metrics using computer vision and OCR techniques.

The application allows users to upload a vehicle image through a React frontend deployed on Vercel, while a FastAPI backend deployed on Render processes the image and returns detailed analysis results. The system performs blur detection, brightness analysis, screenshot detection, duplicate image detection, OCR text extraction, and Indian vehicle number plate validation.

## Live Demo

Frontend:
https://intelligent-media.vercel.app

Backend API:
https://intelligent-media-xz1r.onrender.com

API Documentation:
https://intelligent-media-xz1r.onrender.com/docs

## Features

- Vehicle image upload
- Blur detection using Laplacian variance
- Brightness and low-light analysis
- OCR text extraction using Tesseract OCR
- Indian number plate validation using regex
- Duplicate image detection using perceptual hashing
- Screenshot detection based on image characteristics
- Asynchronous processing with processing IDs
- REST API with Swagger documentation
- Cloud deployment using Vercel and Render

## Tech Stack

Frontend

- React
- Vite
- Axios
- CSS

Backend

- FastAPI
- OpenCV
- NumPy
- Tesseract OCR
- Pillow
- ImageHash
- Uvicorn

Deployment

- Vercel (Frontend)
- Render (Backend)

## Project Structure

```text
intelligent-media-pipeline/
│
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── analysis.py
│   └── database.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── assets/
│   ├── package.json
│   └── vite.config.js
│
├── sample_images/
├── requirements.txt
├── render.yaml
└── README.md
```

## Installation

### Backend Setup

Clone the repository

```bash
git clone https://github.com/Sruthi0704/Intelligent-Media.git
cd Intelligent-Media
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the backend

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

### Frontend Setup

Navigate to the frontend directory

```bash
cd frontend
```

Install dependencies

```bash
npm install
```

Run the frontend

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

## API Endpoints

### Health Check

```http
GET /health
```

### Upload Image

```http
POST /upload
```

Returns a `processing_id`.

### Check Processing Status

```http
GET /status/{processing_id}
```

Returns:

```json
{
  "processing_id": "...",
  "status": "pending | processing | completed | failed"
}
```

### Get Analysis Result

```http
GET /result/{processing_id}
```

Returns:

```json
{
  "processing_id": "...",
  "status": "completed",
  "analysis": {
    "blur_score": 1554.08,
    "is_blurry": false,
    "brightness": 116.70,
    "low_light": false,
    "duplicate": false,
    "ocr_text": "MH12NW8556",
    "number_plate_valid": true,
    "screenshot_suspected": false
  }
}
```

### Get Failure Details

```http
GET /failure/{processing_id}
```

## Image Analysis Pipeline

1. Image upload
2. Blur detection
3. Brightness analysis
4. Image hash generation
5. OCR text extraction
6. Number plate validation
7. Screenshot detection
8. JSON response generation

## OCR and Number Plate Validation

The backend extracts text from uploaded images using Tesseract OCR after image preprocessing techniques such as:

- Grayscale conversion
- Contrast enhancement
- Image resizing
- Sharpening
- Binary thresholding

The extracted text is validated against Indian vehicle number plate formats using regular expressions.

## Deployment

Frontend is deployed on Vercel.

Backend is deployed on Render.

The frontend communicates with the backend using REST APIs over HTTPS.

## Sample Output

```json
{
  "blur_score": 1554.08,
  "is_blurry": false,
  "brightness": 116.70,
  "low_light": false,
  "duplicate": false,
  "ocr_text": "MH12NW8556",
  "number_plate_valid": true,
  "screenshot_suspected": false
}
```

## Author

Sruthi Shakhamuri

GitHub:
https://github.com/Sruthi0704

LinkedIn:
https://www.linkedin.com/in/shakhamuri-sruthi-44a597303
