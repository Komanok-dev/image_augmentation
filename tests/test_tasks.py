import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.tasks import augmentation


# ========================= Test augmentation =======================
@pytest.mark.asyncio
def test_augmentation(
    mock_get_object,
    mock_upload_to_minio,
    mock_sync_sessionmaker,
    mock_db_session,
):
    # Define the input parameters for the augmentation task
    minio_path = "test_bucket/test_image.png"
    filenames = {
        "original": "original_image.png",
        "rotated": "rotated_image.png",
        "gray": "gray_image.png",
        "scaled": "scaled_image.png",
    }
    user_id = "test_user_id"

    # Act: Call the augmentation task
    result = augmentation(
        minio_path=minio_path, filenames=filenames, user_id=user_id, degrees=90
    )

    # Assert: Verify that the result paths match the expected mock URLs
    assert result["rotated_image_path"] == "test_bucket/rotated_image.png"
    assert result["gray_image_path"] == "test_bucket/gray_image.png"
    assert result["scaled_image_path"] == "test_bucket/scaled_image.png"

    # Verify that the MinIO get_object was called correctly
    mock_get_object.assert_called_once_with(
        bucket_name="test_bucket", object_name="test_image.png"
    )

    # Verify that upload_to_minio was called for each transformation
    assert mock_upload_to_minio.call_count == 3

    # Verify that database interactions occurred
    assert (
        mock_db_session.add.call_count == 8
    )  # 2 for the original image, 6 for the transformations
    mock_db_session.commit.assert_called_once()


# # =============== Test augmentation_exception_handling =============


@pytest.mark.asyncio
def test_augmentation_exception_handling(
    mock_get_object,
    mock_upload_to_minio,
    mock_sync_sessionmaker,
    mock_db_session,
):
    # Simulate an exception being raised when adding to the database
    mock_db_session.add.side_effect = SQLAlchemyError(
        "Simulated database error"
    )

    # Define the input parameters for the augmentation task
    minio_path = "test_bucket/test_image.png"
    filenames = {
        "original": "original_image.png",
        "rotated": "rotated_image.png",
        "gray": "gray_image.png",
        "scaled": "scaled_image.png",
    }
    user_id = "test_user_id"

    # Act & Assert: Call the augmentation task and ensure that it raises an exception
    with pytest.raises(SQLAlchemyError, match="Simulated database error"):
        augmentation(
            minio_path=minio_path,
            filenames=filenames,
            user_id=user_id,
            degrees=90,
        )

    mock_db_session.rollback.assert_called_once()
    mock_db_session.commit.assert_not_called()
    mock_sync_sessionmaker.return_value.__exit__.assert_called_once()
