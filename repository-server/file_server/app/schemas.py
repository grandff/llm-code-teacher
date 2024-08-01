from pydantic import BaseModel
from typing import List, Optional

class FileResponse(BaseModel):
    id: int
    file_name: str
    file_path: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    username: str
    gitlab_id: str
    files: Optional[List[FileResponse]] = []

    class Config:
        orm_mode = True