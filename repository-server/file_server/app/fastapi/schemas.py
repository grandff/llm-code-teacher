from pydantic import BaseModel
from typing import List, Optional

class FilesResponse(BaseModel):
    id: int
    file_name: str
    file_path: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    username: str
    gitlab_id: str
    files: Optional[List[FilesResponse]] = []

    class Config:
        orm_mode = True