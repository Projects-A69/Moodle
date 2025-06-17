import uuid
from io import BytesIO


from src.core.config import settings


def upload_image_to_s3(file, folder="profile_pictures"):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    image = Image.open(file.file)
    image = image.convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    filename = f"{folder}/{uuid.uuid4()}.jpg"

    s3.upload_fileobj(
        buffer,
        settings.AWS_BUCKET_NAME,
        filename,
        ExtraArgs={"ContentType": "image/jpeg"},
    )

    return f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
