from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import logging

router = APIRouter()

from models import User, File
from schemas import FileResponse, UserResponse
from database import get_db

# 로그 설정
logger = logging.getLogger(__name__)

@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    try:
        logger.info("Fetching all users with their files")

        # 모든 사용자와 관련된 파일을 쿼리합니다.
        users = db.query(User).options(joinedload(User.files)).all()

        # 응답 객체를 생성하여 반환합니다.
        return users

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

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

