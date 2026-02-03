from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Veo Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "veo_db"
    
    # Gemini AI Configuration
    gemini_api_key: str = ""

    
    class Config:
        env_file = ".env"

settings = Settings()
