from pydantic import BaseModel

class FileResponse(BaseModel):
    id: int
    username: str
    gitlab_id: str
    file_name: str
    file_path: str

    class Config:
        orm_mode = True