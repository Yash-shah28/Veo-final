from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Veo Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "veo_db"
    
    # Gemini AI Configuration (Legacy)
    GEMINI_API_KEY: str = ""
    
    # Hugging Face Inference API Configuration
    HUGGINGFACE_API_KEY: str = ""  # Get from: https://huggingface.co/settings/tokens

    
    class Config:
        env_file = ".env"

settings = Settings()
