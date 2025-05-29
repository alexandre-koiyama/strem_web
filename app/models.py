# app/models.py
from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Indexed for faster lookups
    hashed_password = Column(String)

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    stream_url = Column(String)
    group = Column(String)  # <-- Add this line
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="cameras")
    videos = relationship("Video", back_populates="camera")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    file_path = Column(String)
    camera_id = Column(Integer, ForeignKey("cameras.id"))

    camera = relationship("Camera", back_populates="videos")

# Update User relationship
User.cameras = relationship("Camera", back_populates="owner")