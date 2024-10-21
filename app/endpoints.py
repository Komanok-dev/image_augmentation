import asyncio
import io
import zipfile
from pathlib import Path
from typing import Annotated, List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.auth import UserAuthorization, get_password_hash, user_authorization
from app.database import DatabaseSession
from app.minio_client import minio_client, upload_to_minio
from app.models import ImageTask, User
from app.schemas import UserLogin, UserRegister, UserHistory
from app.tasks import augmentation

router = APIRouter(tags=["API"])


@router.post("/registration")
async def register_user(
    form_data: Annotated[UserRegister, Depends()], session: DatabaseSession
) -> str:
    new_user = User(
        email=form_data.email,
        password=get_password_hash(form_data.password),
        first_name=form_data.first_name,
        last_name=form_data.last_name,
    )
    session.add(new_user)
    await session.commit()
    return await user_authorization(session=session, form_data=form_data)


@router.post("/login")
async def login_user(
    form_data: Annotated[UserLogin, Depends()], session: DatabaseSession
) -> str:
    return await user_authorization(session=session, form_data=form_data)


@router.post("/upload")
async def upload_images(
    user: UserAuthorization, files: List[UploadFile] = File(...)
) -> dict:
    async def handle_file(file: UploadFile):
        path = Path(file.filename)
        filename, file_extension = path.stem, path.suffix.lower().lstrip(".")
        filenames = {
            "original": f"{filename}_original.{file_extension}",
            "rotated": f"{filename}_rotated.{file_extension}",
            "gray": f"{filename}_gray.{file_extension}",
            "scaled": f"{filename}_scaled.{file_extension}",
        }
        original_minio_path = upload_to_minio(
            file=file.file, filename=filenames["original"]
        )
        augmentation_task = augmentation.delay(
            minio_path=original_minio_path,
            filenames=filenames,
            user_id=user.id,
        )
        return {
            "file": file.filename,
            "augmentation_task_id": augmentation_task.id,
        }

    tasks = [handle_file(file) for file in files]
    results = await asyncio.gather(*tasks)

    return results


@router.get("/status/{task_id}")
async def get_task_status(task_id: str, user: UserAuthorization) -> dict:
    task_result = AsyncResult(task_id)
    return {"status": task_result.state}


@router.get("/history/{user_id}")
async def get_user_history(
    session: DatabaseSession,
    user: UserAuthorization,
    user_id: str,
) -> list[dict]:
    result = await session.execute(select(ImageTask).where(User.id == user_id))
    images = result.scalars().all()

    if not images:
        raise HTTPException(
            status_code=404, detail="No history found for the given user ID"
        )
    return images


@router.get("/task/{task_id}")
async def get_task_images(
    session: DatabaseSession,
    user: UserAuthorization,
    task_id: str,
    bucket_name="images",
) -> StreamingResponse:
    result = await session.execute(
        select(ImageTask).where(ImageTask.task_id == task_id)
    )
    images = result.scalars().all()

    if not images:
        raise HTTPException(
            status_code=404, detail="No images found for the given task ID"
        )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for image in images:
            response = minio_client.get_object(
                bucket_name=bucket_name, object_name=image.img_link
            )
            file_data = response.read()
            response.close()
            response.release_conn()
            zip_file.writestr(image.img_link, file_data)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={task_id}_images.zip"
        },
    )
