from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your router
from app.routes import router

app = FastAPI(
    title="Intelligent Media Processing Pipeline",
    version="1.0",
    description="Upload vehicle images and perform OCR, blur detection, brightness analysis, duplicate detection, and screenshot detection."
)

# Allow frontend origins
origins = [
    "http://localhost:5173",              # Local Vite frontend
    "http://127.0.0.1:5173",              # Local Vite frontend (127.0.0.1)
    "https://intelligent-media.vercel.app",  # Your deployed Vercel frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Intelligent Media Processing Pipeline API is running",
        "docs": "/docs",
        "health": "/health"
    }

# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Intelligent Media Processing Pipeline"
    }