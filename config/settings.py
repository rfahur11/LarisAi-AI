from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "LarisAI - AI Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017" # Default, overridden by docker-compose
    MONGODB_DB_NAME: str = "larisai"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    # WA Gateway (Mock by default)
    WA_GATEWAY_URL: str = ""
    WA_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
