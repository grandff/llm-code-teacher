from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import FileResponse
from typing import List
import logging
import os
from models import User, Files
from schemas import FilesResponse, UserResponse
from database import get_db
from sqlalchemy.exc import IntegrityError

# 라우트 설정
router = APIRouter()

# 다운로드할 파일의 저장 위치
SHARED_FILES_DIR = "/shared_files"  # 실제 공유 파일 경로로 설정

# 로그 설정
logger = logging.getLogger(__name__)

@router.get("/test")
def get_test():
    return {"Hello": "test router"}

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

#파일 다운로드 
@router.get("/download/{path:path}", response_class=FileResponse)
def download_file(path: str):
    try:
        # 파일이 저장된 경로를 결합합니다.
        file_path = os.path.join(SHARED_FILES_DIR, path)

        # 디버깅을 위해 경로를 로그로 출력합니다
        logger.info(f"Resolved file path: {file_path}")

        # 파일이 존재하지 않는 경우
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist")
            raise HTTPException(status_code=404, detail="File not found")

        logger.info(f"Serving file {file_path}")
        return FileResponse(file_path, filename=os.path.basename(file_path))

    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File download failed")
    

# 파일 업로드
@router.post("/upload/{username}/{git_id}/")   
async def upload_file(username: str, git_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # 디렉토리 경로 생성
        directory_path = os.path.join(SHARED_FILES_DIR, username, git_id)
        os.makedirs(directory_path, exist_ok=True)

        # 파일 저장 경로
        file_location = os.path.join(directory_path, file.filename)

        # 파일 저장
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # 사용자 확인 및 추가
        user = db.query(User).filter_by(username=username, gitlab_id=git_id).first()
        if not user:
            # 사용자 추가
            user = User(username=username, gitlab_id=git_id)
            db.add(user)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                # 이미 존재할 경우 에러 처리
                user = db.query(User).filter_by(username=username, gitlab_id=git_id).first()
        
        # 파일 정보 데이터베이스에 추가
        db_file = Files(user_id=user.id, file_name=file.filename, file_path=file_location)
        db.add(db_file)
        db.commit()


        logger.info(f"file '{file.filename}' saved at '{directory_path}'")
        return {"info": f"file '{file.filename}' saved at '{directory_path}'"}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")
    