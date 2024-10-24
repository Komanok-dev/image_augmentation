from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from app.minio_client import minio_client
from app.models import Base


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest_asyncio.fixture
async def mock_async_db_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_minio_client():
    with patch("app.minio_client.minio_client") as mock_client:
        yield mock_client


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session


# ++++++++++++++++++++++++++++++++++++++++


@pytest.fixture
def mock_image_response():
    """Creates a mock response for an image download from MinIO."""
    mock_response = MagicMock()
    image = Image.new("RGB", (100, 100), color="red")
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    mock_response.read.return_value = image_bytes.getvalue()
    return mock_response


@pytest.fixture
def mock_get_object(mock_image_response):
    """Patches the MinIO get_object method."""
    with patch.object(
        minio_client, "get_object", return_value=mock_image_response
    ) as mock:
        yield mock


@pytest.fixture
def mock_upload_to_minio():
    """Mocks the upload_to_minio function."""
    with patch("app.tasks.upload_to_minio") as mock:
        mock.side_effect = (
            lambda file, filename, bucket_name: f"{bucket_name}/{filename}"
        )
        yield mock


@pytest.fixture
def mock_sync_sessionmaker(mock_db_session):
    """Patches the sync_sessionmaker to return a mock session."""
    with patch("app.tasks.sync_sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value.__enter__.return_value = mock_db_session
        yield mock_sessionmaker
