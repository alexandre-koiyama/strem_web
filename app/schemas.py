# app/schemas.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


class CameraBase(BaseModel):
    name: str
    stream_url: str

class CameraCreate(CameraBase):
    pass

class VideoBase(BaseModel):
    title: str
    file_path: str

class VideoCreate(VideoBase):
    camera_id: int