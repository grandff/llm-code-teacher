import logging
from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from models import WebHookResponse, ErrorResponse, PromptCreateRequest, PromptCreateRequestV1
from dotenv import load_dotenv
import os
import git
from urllib.parse import urlparse
from celery_app import llm_code_review_task
from services.create_prompt import create_prompt, create_prompt_v1
import shutil
import time
from services.convert_char import convert_to_english
import subprocess

# .env 파일에서 환경 변수 로드
load_dotenv()

router = APIRouter()

# 로컬 리포지토리 경로 설정
LOCAL_REPO_PATH = os.getenv('LOCAL_REPO_PATH', "/tmp/repo")
# 퍼스널 액세스 토큰 또는 SSH 키 사용 시 필요
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', "") 
# gitlab reverse proxy
PROEJCT_CONTEXT_PATH = os.getenv('PROEJCT_CONTEXT_PATH', "")

@router.post("/git/webhook")
async def gitlab_webhook(request : Request):        
    payload = await request.json()
    print(payload)
    
    # 필요한 정보를 추출
    user_name = payload['user_username']
    user_name = convert_to_english(user_name)   # 영어로 변환
    
    project_info = payload['project']
    project_url= project_info['http_url']
    # URL 파싱
    parsed_url = urlparse(project_url)
    # 경로 추출
    extracted_part = parsed_url.path
    repo_url = f"http://oauth2:{ACCESS_TOKEN}@{PROEJCT_CONTEXT_PATH}{extracted_part}"
    
    commit_sha = payload['checkout_sha']
    commits = payload['commits']
    
    if not os.path.exists(LOCAL_REPO_PATH) :
        # 레포지토리 정보가 없다면 클론
        repo = git.Repo.clone_from(repo_url, LOCAL_REPO_PATH)
    else :
        # 이미 존재하는 경우 변경 사항만 가져옴        
        repo = git.Repo(LOCAL_REPO_PATH)
        repo.git.checkout(commit_sha)
    #     logging.error(e)
    #     # 로컬 디렉토리 정리
    #     if os.path.exists(LOCAL_REPO_PATH):
    #         shutil.rmtree(LOCAL_REPO_PATH)
    #     # 리포지토리 클론
    #     repo = git.Repo.clone_from(repo_url, LOCAL_REPO_PATH)
    #     # 특정 커밋으로 체크아웃
    #     repo.git.checkout(commit_sha)
        
    try :                
        # 수정된 파일 목록 가져오기 및 파일 내용 읽기
        for commit in commits:                                    
            # 추가된 파일
            for file_path in commit["added"]:
                absolute_file_path = os.path.join(LOCAL_REPO_PATH, file_path)                
                # 파일 디렉토리가 존재하는지 확인하고 파일 내용 읽기
                if os.path.exists(absolute_file_path):
                    with open(absolute_file_path, 'r') as file:
                        commit_file_str = file.read()
                        file_ext = os.path.splitext(file_path)[1]
                        request = PromptCreateRequestV1(file_ext=file_ext, file_name = file_path, file_data=commit_file_str,)
                        # LLM 분석 요청
                        add_task_to_llm_v1(request, user_name)
                # 1초 딜레이
                time.sleep(1)
                                                          
            # 수정된 파일
            for file_path in commit["modified"]:
                absolute_file_path = os.path.join(LOCAL_REPO_PATH, file_path)

                # 파일 디렉토리가 존재하는지 확인하고 파일 내용 읽기
                if os.path.exists(absolute_file_path):
                    with open(absolute_file_path, 'r') as file:
                        modified_file_str = file.read()
                        file_ext = os.path.splitext(file_path)[1]
                        request = PromptCreateRequestV1(file_ext=file_ext, file_name = file_path, file_data=modified_file_str,)
                        # LLM 분석 요청
                        add_task_to_llm_v1(request, user_name)
                # 1초 딜레이
                time.sleep(1)
                                          
    except Exception as e:
        logging.error(e)
        response = ErrorResponse(detail=str(e)) 
        return JSONResponse(status_code=400, content=response.model_dump())            
    return JSONResponse(status_code=200, content={"detail" : "ok"})

# LLM 분석 요청 v1
def add_task_to_llm_v1(request : PromptCreateRequestV1, user_name : str ) :
    # 프롬프트 생성
    user_prompt = create_prompt_v1(request)
    # Celery에 작업 등록
    task = llm_code_review_task.apply_async(args=[user_prompt, user_name ])    
    print(task.id)    