"""
ReLife AI — Centralized configuration loaded from environment.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists (local development)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    # AWS
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "")

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Groq AI (lifecycle)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def use_mock_db(self) -> bool:
        return not self.MONGO_URI

    @property
    def cors_origins(self) -> list[str]:
        if self.is_production:
            return [self.FRONTEND_URL]
        return ["*"]


settings = Settings()
