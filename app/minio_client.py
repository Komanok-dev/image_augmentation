from typing import BinaryIO

from minio import Minio

from app.settings import minio_settings

minio_client = Minio(
    minio_settings.url,
    access_key=minio_settings.ROOT_USER,
    secret_key=minio_settings.ROOT_PASSWORD,
    secure=False,
)


def upload_to_minio(
    file: BinaryIO, filename: str, bucket_name: str = "images"
) -> str:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    file.seek(0)
    minio_client.put_object(
        bucket_name, filename, file, length=-1, part_size=10 * 1024 * 1024
    )
    return f"{bucket_name}/{filename}"
