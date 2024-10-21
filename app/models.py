from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
)

Base = declarative_base()


class ImageTask(Base):
    __tablename__ = "imagetask"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    img_link: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    stats: Mapped["Stats"] = relationship(
        "Stats", back_populates="image", uselist=False
    )
    user: Mapped["User"] = relationship("User", back_populates="tasks")


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    tasks: Mapped[List["ImageTask"]] = relationship(
        "ImageTask", back_populates="user"
    )


class Stats(Base):
    __tablename__ = "stats"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    image_id: Mapped[UUID] = mapped_column(
        ForeignKey("imagetask.id", ondelete="CASCADE"), nullable=False
    )
    image: Mapped["ImageTask"] = relationship(
        "ImageTask", back_populates="stats"
    )
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_time: Mapped[float] = mapped_column(Integer, nullable=False)
