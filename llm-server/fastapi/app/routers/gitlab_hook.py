from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from models import WebHookResponse, ErrorResponse, PromptCreateRequest
from dotenv import load_dotenv
import os
import git
from urllib.parse import urlparse
from celery_app import llm_code_review_task
from services.create_prompt import create_prompt

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
    project_info = payload['project']
    project_url= project_info['http_url']
    # URL 파싱
    parsed_url = urlparse(project_url)
    # 경로 추출
    extracted_part = parsed_url.path
    repo_url = f"http://oauth2:{ACCESS_TOKEN}@{PROEJCT_CONTEXT_PATH}{extracted_part}"
    
    commit_sha = payload['checkout_sha']
    commits = payload['commits']
    
    # 각각 커밋 제목, 내용, 추가, 수정 파일 목록을 저장할 딕셔너리    
    commit_id_list = []
    title_dict = {}
    message_dict = {}    
    added_files_content = {}
    modified_files_content = {}    
    
    try :
        ## FIXME 이부분 지금 오류남
        if not os.path.exists(LOCAL_REPO_PATH) :
            # 레포지토리 정보가 없다면 클론
            repo = git.Repo.clone_from(repo_url, LOCAL_REPO_PATH)
        else :
            # 이미 존재하는 경우 변경 사항만 가져옴
            repo = git.Repo(LOCAL_REPO_PATH)
            origin = repo.remotes.origin
            origin.pull()
                    
        # 특정 커밋으로 체크아웃
        repo.git.checkout(commit_sha)
        
        # 수정된 파일 목록 가져오기 및 파일 내용 읽기
        for commit in commits:            
            commit_id = commit["id"]    # commit id
            commit_title = commit["title"]  # title
            commit_message = commit["message"] # message
            
            # 제목과 타이틀 저장            
            commit_id_list.append(commit_id)
            title_dict[commit_id] = commit_title
            message_dict[commit_id] = commit_message          
            
            # 추가된 파일
            for file_path in commit["added"]:
                absolute_file_path = os.path.join(LOCAL_REPO_PATH, file_path)
                
                # 파일 디렉토리가 존재하는지 확인하고 파일 내용 읽기
                if os.path.exists(absolute_file_path):
                    with open(absolute_file_path, 'r') as file:
                        added_files_content[file_path] = file.read()                                                        
            # 수정된 파일
            for file_path in commit["modified"]:
                absolute_file_path = os.path.join(LOCAL_REPO_PATH, file_path)

                # 파일 디렉토리가 존재하는지 확인하고 파일 내용 읽기
                if os.path.exists(absolute_file_path):
                    with open(absolute_file_path, 'r') as file:
                        modified_files_content[file_path] = file.read()                                        
    except Exception as e:
        response = ErrorResponse(detail=str(e)) 
        return JSONResponse(status_code=400, content=response.model_dump())        
    
    # prompt 생성
    request = PromptCreateRequest(id_list=commit_id_list, title_dict=title_dict, message_dict=message_dict, added_files_content=added_files_content, modified_files_content=modified_files_content)
    user_prompt = create_prompt(request)
    print(user_prompt)
    task = llm_code_review_task.apply_async(args=[user_prompt])
    print(task.id)    
    return JSONResponse(status_code=200, content={"detail" : task.id})
