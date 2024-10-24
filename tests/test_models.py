from datetime import datetime
from uuid import uuid4

from sqlalchemy.future import select

from app.models import ImageTask, Stats, User

# =========================== Test add User =========================


def test_create_user(session):
    user = User(
        id=uuid4(),
        email="test@example.com",
        password="securepassword",
        first_name="John",
        last_name="Doe",
        created_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()

    result = session.execute(
        select(User).where(User.email == "test@example.com")
    ).scalar_one()

    assert result.email == "test@example.com"
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.password == "securepassword"


# ========================= Test add Imagetask =======================


def test_create_imagetask(session):
    user = User(
        id=uuid4(),
        email="test_user@example.com",
        password="securepassword",
        first_name="Jane",
        last_name="Doe",
        created_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()

    image_task = ImageTask(
        id=uuid4(),
        task_id=uuid4(),
        user_id=user.id,
        img_link="https://example.com/image.png",
        created_at=datetime.utcnow(),
    )
    session.add(image_task)
    session.commit()

    result = session.execute(
        select(ImageTask).where(ImageTask.user_id == user.id)
    ).scalar_one()
    assert result.img_link == "https://example.com/image.png"
    assert result.user == user


# =========================== Test add Stats =========================


def test_create_stats(session):
    user = User(
        id=uuid4(),
        email="test_stats_user@example.com",
        password="securepassword",
        first_name="Anna",
        last_name="Smith",
        created_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()

    image_task = ImageTask(
        id=uuid4(),
        task_id=uuid4(),
        user_id=user.id,
        img_link="https://example.com/another_image.png",
        created_at=datetime.utcnow(),
    )
    session.add(image_task)
    session.commit()

    stats = Stats(
        id=uuid4(),
        image_id=image_task.id,
        width=1920,
        height=1080,
        size=512345,
        processing_time=1.23,
    )
    session.add(stats)
    session.commit()

    result = session.execute(
        select(Stats).where(Stats.image_id == image_task.id)
    ).scalar_one()
    assert result.width == 1920
    assert result.height == 1080
    assert result.size == 512345
    assert result.processing_time == 1.23
    assert result.image == image_task
