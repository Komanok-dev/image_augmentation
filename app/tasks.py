import io
from time import time

from PIL import Image

from app.celery import celery_app
from app.database import sync_sessionmaker
from app.minio_client import minio_client, upload_to_minio
from app.models import ImageTask, Stats


@celery_app.task(bind=True)
def augmentation(
    self, minio_path: str, filenames: dict, user_id: str, degrees: int = 90
) -> dict:
    """
    Rotates, converts to grayscale, and resizes images, while measuring processing time for each operation.
    Saves each transformed image to MinIO and records metadata in the database.

    Args:
        minio_path (str): The path to the MinIO storage where images are stored.
        filenames (dict): A dictionary containing image filenames and their corresponding details.
        user_id (str): The ID of the user who initiated the task.
        degrees (int): The degree by which to rotate the images. Default is 90 degrees.

    Returns:
        dict: A dictionary containing the paths of the transformed images saved in MinIO,
              with keys formatted as "{operation}_image_path".
    """

    task_id = self.request.id

    with sync_sessionmaker() as session:
        try:
            # Extract the bucket name and object name from minio_path
            bucket_name, object_name = minio_path.split("/", 1)

            # Download the image from MinIO
            response = minio_client.get_object(
                bucket_name=bucket_name, object_name=object_name
            )
            file_data = io.BytesIO(response.read())
            response.close()
            response.release_conn()

            # Open the image using PIL
            image = Image.open(file_data)

            width, height = image.size
            original_format = image.format

            # Add original image stats to database session
            new_image = ImageTask(
                task_id=task_id,
                user_id=user_id,
                img_link=filenames["original"],
            )
            session.add(new_image)
            session.flush()
            session.add(
                Stats(
                    image_id=new_image.id,
                    width=width,
                    height=height,
                    size=file_data.tell(),
                    processing_time=0,
                )
            )

            processing_times = {}

            # Perform image transformations
            start_time = time()
            rotated_image = image.rotate(degrees, expand=True)
            processing_times["rotated"] = time() - start_time

            start_time = time()
            gray_image = image.convert("L")
            processing_times["gray"] = time() - start_time

            start_time = time()
            gray_scaled = image.resize((image.width // 2, image.height // 2))
            processing_times["scaled"] = time() - start_time

            transformations = {
                "rotated": rotated_image,
                "gray": gray_image,
                "scaled": gray_scaled,
            }

            # Save each transformed image to MinIO and add to the database session
            result_paths = {}
            for key, transformed_image in transformations.items():
                img_byte_arr = io.BytesIO()
                transformed_image.save(img_byte_arr, format=original_format)
                width, height = transformed_image.size
                img_byte_arr.seek(0)
                result_paths[f"{key}_image_path"] = upload_to_minio(
                    img_byte_arr, filenames[key], bucket_name=bucket_name
                )
                new_image = ImageTask(
                    task_id=task_id, user_id=user_id, img_link=filenames[key]
                )
                session.add(new_image)
                session.flush()
                session.add(
                    Stats(
                        image_id=new_image.id,
                        width=width,
                        height=height,
                        size=img_byte_arr.tell(),
                        processing_time=processing_times[key],
                    )
                )

            # Commit all changes to the database
            session.commit()

            return result_paths
        except Exception as e:
            session.rollback()
            raise e
