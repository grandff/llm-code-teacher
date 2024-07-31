from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

router = APIRouter()


from models import File
from schemas import FileResponse
from database import get_db

# 로그 설정
logger = logging.getLogger(__name__)


#파일 전체 조회
@router.get("/files", response_model=List[FileResponse])
def read_files(db: Session = Depends(get_db)):
    try:
        logger.info('files = db.query(File).all() 실행')
        files = db.query(File).all()
        logger.info(files)
        return files
    except Exception as e:
        logger.error(f"Error fetching files: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
