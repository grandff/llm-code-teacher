from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any
from models import User, Files
from schemas import FilesResponse, UserResponse
from database import get_db
from datetime import datetime, timezone
import logging
import os
import urllib.parse



# 라우트 설정
router = APIRouter()

# 다운로드할 파일의 저장 위치
SHARED_FILES_DIR = "/shared_files"  # 실제 공유 파일 경로로 설정

# 로그 설정
logger = logging.getLogger(__name__)

@router.get("/test")
def get_test():
    return {"Hello": "test router"}

# 파일 업로드
@router.post("/upload/")   
async def upload_file(
    username: str = Body(...),  
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        logger.info("@router.post upload come")

        # 현재 날짜를 YYYYMMDD 형식으로 가져오기
        current_date = datetime.now(timezone.utc).strftime('%Y%m%d')

        # 디렉토리 경로 생성
        directory_path = os.path.join(SHARED_FILES_DIR, current_date, username)
        os.makedirs(directory_path, exist_ok=True)

        file_location = os.path.join(directory_path, file.filename)

        # 사용자 확인 및 추가
        user = db.query(User).filter_by(username=username).first()
        
        # 수정: 사용자 존재 여부 확인 및 새로운 사용자 생성
        if not user:
            user = User(username=username)
            db.add(user)
            try:
                db.commit()        
                # 사용자 객체를 새로 조회하여 ID 확인
                user = db.query(User).filter_by(username=username).first()
                if not user:
                    raise HTTPException(status_code=500, detail="Failed to retrieve user after commit")
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=500, detail="Failed to retrieve user after rollback")

        # 기존 파일 정보 삭제 (경로가 동일한 경우)
        existing_file = db.query(Files).filter_by(user_id=user.id, file_path=file_location).first()
        if existing_file:
            db.delete(existing_file)
            db.commit()  # 변경 사항 커밋

        db_file = Files(user_id=user.id, file_name=file.filename, file_path=file_location)
        db.add(db_file)
        db.commit()

        # 파일 저장
        with open(file_location, "wb") as f:
            f.write(await file.read())

        logger.info(f"file '{file.filename}' saved at '{directory_path}'")
        return {"info": f"file '{file.filename}' saved at '{directory_path}'"}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")   

#파일 다운로드 
@router.get("/download/{path:path}", response_class=FileResponse)
def download_file(path: str):
    try:
        # 파일이 저장된 경로를 결합합니다.
        file_path = os.path.join("/", path)
        logger.error(f"File name : {file_path}")
        
        # 파일이 존재하지 않는 경우
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist")
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, filename=os.path.basename(file_path))

    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File download failed")


# 파일 및 디렉토리 목록 조회
@router.get("/list_files", response_model=Dict[str, Any])
def list_files(db: Session = Depends(get_db)):
    try:
        directory_contents = list_files_in_directory(SHARED_FILES_DIR)
        return directory_contents
    except Exception as e:
        logger.error(f"Error listing files in directory: {e}")
        raise HTTPException(status_code=500, detail="Error listing files in directory")


def list_files_in_directory(directory_path: str) -> Dict[str, Any]:
    """주어진 디렉토리의 파일 및 디렉토리 목록을 재귀적으로 반환합니다."""
    result = {"path": directory_path, "files": [], "directories": []}
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                result["files"].append(item)
            elif os.path.isdir(item_path):
                result["directories"].append(list_files_in_directory(item_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files in directory: {str(e)}")
    return result

#사용자별 파일 조회
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
@router.get("/files", response_model=List[FilesResponse])
def read_files(db: Session = Depends(get_db)):
    try:
        logger.info('files = db.query(File).all() 실행')
        files = db.query(Files).all()
        logger.info(files)
        return files
    except Exception as e:
        logger.error(f"Error fetching files: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    