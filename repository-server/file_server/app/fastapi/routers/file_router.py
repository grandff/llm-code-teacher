from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, func
from typing import List, Dict, Any, Union
from models import User, Files
from schemas import FilesResponse, UserResponse
from database import get_db
from datetime import datetime, timezone
import logging
import os
from PyPDF2 import PdfReader
import urllib.parse



# 라우트 설정
router = APIRouter()

# 다운로드할 파일의 저장 위치
SHARED_FILES_DIR = "/shared_files"  # 실제 공유 파일 경로로 설정

# 로그 설정
logging.basicConfig(
    level=logging.INFO,  # 로그 수준 설정
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/supervisor/fastapi.log'),  # 로그 파일 경로
        logging.StreamHandler()  # 콘솔에 로그 출력
    ]
)
logger = logging.getLogger(__name__)

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


#사용 가능한 날짜 목록을 반환
@router.get("/available_dates", response_model=Dict[str, List[str]])
def get_available_dates(db: Session = Depends(get_db)):
    try:
        logger.info("Fetching available dates")

        # 직접 SQL 쿼리 실행
        query = "SELECT DISTINCT DATE_FORMAT(created_at, '%Y%m%d') AS date FROM files ORDER BY date DESC"
        result = db.execute(query)
        dates = result.fetchall()

        # 날짜 리스트 생성
        available_dates = [date[0] for date in dates]
        logger.info(f"Available dates: {available_dates}")

        # 딕셔너리 형식으로 반환
        return {"dates": available_dates}

    except Exception as e:
        logger.error(f"Error fetching available dates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available dates")


# 선택된 날짜에 대한 사용자들의 리스트를 반환
@router.get("/users_for_date", response_model=Dict[str, List[Dict[str, Any]]])
def get_users_for_date(selected_date: str, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching users for date: {selected_date}")

        # 서브쿼리 정의
        subquery = (
            db.query(Files.user_id)
            .filter(func.date_format(Files.created_at, '%Y%m%d') == selected_date)
            .distinct()
            .subquery()
        )

        # 메인 쿼리
        users = (
            db.query(User.username, User.id)
            .join(subquery, User.id == subquery.c.user_id)
            .all()
        )
        
        # 결과를 JSON 형식으로 변환하여 반환
        result_list = [{"username": user.username, "id": user.id} for user in users]
        return {"userList": result_list}

    except Exception as e:
        logger.error(f"Error fetching users for date {selected_date}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")
    


# # 선택된 날짜에 대한 파일 목록을 조회하는 함수
@router.get("/files_for_date", response_model=Dict[str, List[Dict[str, Any]]])
def get_files_for_date(selected_date: str, user_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching files for date {selected_date} and user_id {user_id}")

        files = (
            db.query(Files)
            .filter(func.date(Files.created_at) == selected_date, Files.user_id == user_id)
            .all()
        )

        # 결과를 JSON 형식으로 변환하여 반환
        file_list = [{"file_name": file.file_name, "file_path": file.file_path, "created_at": file.created_at} for file in files]
        return {"fileList": file_list}

    except Exception as e:
        logger.error(f"Error fetching files for date {selected_date} and user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")



# 파일 미리보기 함수
@router.get("/preview_file/")
async def preview_file(file_path: str, db: Session = Depends(get_db)) -> Union[str, dict]:
    try:
        # 실제 파일 경로를 결합
        #full_file_path = os.path.join(SHARED_FILES_DIR, file_path)
        full_file_path = file_path
        
        logger.info(f"Request to preview file: {full_file_path}")

        # 파일이 존재하는지 확인
        if not os.path.exists(full_file_path):
            logger.error(f"File {full_file_path} does not exist")
            raise HTTPException(status_code=404, detail="File not found")

        # 파일의 확장자에 따라 콘텐츠를 생성
        file_extension = os.path.splitext(full_file_path)[1].lower()
        
        if file_extension == ".txt":
            # 텍스트 파일을 읽고 인코딩 후 iframe으로 미리 보기
            with open(full_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            encoded_content = content.replace("\n", "%0A").replace(" ", "%20").replace("'", "%27").replace('"', "%22")
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <title>텍스트 파일 미리보기</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background-color: #f4f4f4;
                    }}
                    iframe {{
                        width: 100%;
                        height: 100%;
                        border: none;
                    }}
                </style>
            </head>
            <body>
                <iframe src="data:text/plain;charset=utf-8,{encoded_content}"></iframe>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        elif file_extension == ".pdf":
            file_url = f"http://localhost:9501/exists_files{file_path}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <title>PDF 파일 미리보기</title>
                <style>
                    html, body {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }}
                    iframe {{
                        border: none;
                        width: 100vw;  /* 전체 뷰포트 너비 */
                        height: 100vh; /* 전체 뷰포트 높이 */
                    }}
                </style>
            </head>
            <body>
                <iframe src="{file_url}"></iframe>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
            
        elif file_extension in [".xls", ".xlsx"]:
            import pandas as pd
            df = pd.read_excel(full_file_path)
            html_table = df.to_html(classes='table table-striped', index=False)
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <title>엑셀 파일 미리보기</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background-color: #f4f4f4;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                </style>
            </head>
            <body>
                {html_table}
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        
        elif file_extension in [".jpg", ".jpeg", ".png", ".gif"]:  # 이미지 파일 확장자 확인
            file_url = f"http://localhost:9501/exists_files{file_path}"
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <title>이미지 파일 미리보기</title>
                <style>
                    html, body {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        background-color: #f0f0f0; /* 배경색 설정 */
                    }}
                    img {{
                        max-width: 100%;  /* 이미지 최대 너비 */
                        max-height: 100%; /* 이미지 최대 높이 */
                    }}
                </style>
            </head>
            <body>
                <img src="{file_url}" alt="이미지 미리보기" />
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type for preview")
    
    except Exception as e:
        logger.error(f"Error previewing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File preview failed")
    


@router.get("/exists_files/{file_path:path}")
async def get_shared_file(file_path: str):
    logger.info(f"file_path: {file_path}")
    full_file_path = os.path.join("/", file_path)
    logger.info(f"full_file_path: {full_file_path}")

    if os.path.exists(full_file_path):
        return FileResponse(full_file_path)
    else:
        return {"detail": "File not found"}