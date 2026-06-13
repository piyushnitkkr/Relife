"""
ReLife AI — Centralized configuration loaded from environment.
Uses .env locally, environment variables on EC2/Lambda.
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
    S3_BUCKET: str = os.getenv("S3_BUCKET", "relife-ai-assets")
    DYNAMO_TABLE_NAME: str = os.getenv("DYNAMO_TABLE_NAME", "relife-user-credits")
    SNS_TOPIC_ARN: str = os.getenv("SNS_TOPIC_ARN", "")

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "")

    # Cognito
    COGNITO_USER_POOL_ID: str = os.getenv("COGNITO_USER_POOL_ID", "")
    COGNITO_APP_CLIENT_ID: str = os.getenv("COGNITO_APP_CLIENT_ID", "")
    COGNITO_REGION: str = os.getenv("COGNITO_REGION", "us-east-1")

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
        """Use in-memory mock when no MongoDB URI is configured."""
        return not self.MONGO_URI

    @property
    def cors_origins(self) -> list[str]:
        if self.is_production:
            return [self.FRONTEND_URL]
        return ["*"]


settings = Settings()
