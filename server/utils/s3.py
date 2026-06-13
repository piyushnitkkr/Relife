"""S3 utility — upload product images. Free: 5 GB storage."""
import uuid
from config import settings

try:
    import boto3
    _s3 = boto3.client("s3", region_name=settings.AWS_REGION)
except Exception:
    _s3 = None


def upload_image(image_bytes: bytes, filename: str, folder: str = "returns") -> str:
    """
    Upload image to S3. Returns the public URL.
    Falls back to empty string if S3 not configured.
    """
    if not _s3 or not settings.S3_BUCKET:
        return ""

    key = f"{folder}/{uuid.uuid4()}-{filename}"
    _s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=image_bytes,
        ContentType="image/jpeg",
    )
    return f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{key}"
