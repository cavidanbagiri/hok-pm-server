# models.py (fixed)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base


class StatusModel(Base):
    __tablename__ = "status"
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)

    def __str__(self) -> str:
        return self.status


class ProjectModel(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    code = Column(String, nullable=False)


class ImageModel(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    image = relationship("ImageModel")
    status = relationship("StatusModel")
    project = relationship("ProjectModel")
    tokens = relationship("TokenModel", back_populates="user")


class TokenModel(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(String(500), unique=True, nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="tokens")