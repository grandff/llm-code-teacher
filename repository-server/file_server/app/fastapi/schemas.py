from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FilesResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    username: str
    files: Optional[List[FilesResponse]] = []

    class Config:
        orm_mode = True