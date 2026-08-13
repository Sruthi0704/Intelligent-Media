from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routes import router

# Create FastAPI app first
app = FastAPI(
    title="Intelligent Media Processing Pipeline",
    version="1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Media Processing Pipeline API is running"}