from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from config.database import Database
import mlflow

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Dibatasi hanya untuk frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    # Initialize DB connection on startup
    Database.get_db()
    # Set up MLflow tracking URI
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)

from routers.ai_router import router as ai_router

@app.on_event("shutdown")
async def shutdown_db_client():
    Database.close()

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

# Mendaftarkan seluruh rute AI
app.include_router(ai_router, prefix=settings.API_V1_STR)
