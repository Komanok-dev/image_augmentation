from io import BytesIO
from unittest.mock import MagicMock

from app.minio_client import upload_to_minio

# ======================== Test upload_to_minio ======================


def test_upload_to_minio_existing_bucket(mock_minio_client):
    mock_minio_client.bucket_exists.return_value = True
    mock_minio_client.make_bucket = MagicMock()
    mock_minio_client.put_object = MagicMock()
    file = BytesIO(b"file content")
    filename = "test_image.png"
    bucket_name = "images"
    result = upload_to_minio(file, filename, bucket_name)
    mock_minio_client.bucket_exists.assert_called_once_with(bucket_name)
    mock_minio_client.make_bucket.assert_not_called()
    mock_minio_client.put_object.assert_called_once_with(
        bucket_name, filename, file, length=-1, part_size=10 * 1024 * 1024
    )
    assert result == f"{bucket_name}/{filename}"


def test_upload_to_minio_new_bucket(mock_minio_client):
    mock_minio_client.bucket_exists.return_value = False
    mock_minio_client.make_bucket = MagicMock()
    mock_minio_client.put_object = MagicMock()

    file = BytesIO(b"file content")
    filename = "test_image.png"
    bucket_name = "new-bucket"

    result = upload_to_minio(file, filename, bucket_name)

    mock_minio_client.bucket_exists.assert_called_once_with(bucket_name)
    mock_minio_client.make_bucket.assert_called_once_with(bucket_name)
    mock_minio_client.put_object.assert_called_once_with(
        bucket_name, filename, file, length=-1, part_size=10 * 1024 * 1024
    )
    assert result == f"{bucket_name}/{filename}"
