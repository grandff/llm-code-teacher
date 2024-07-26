**분석 요약:** GitLab 웹훅을 처리하고 코드 리뷰를 위한 프롬프트를 생성하는 FastAPI 애플리케이션입니다. 로컬로 저장소를 클론하고 커밋 내용을 읽어 프롬프트에 추가합니다.

**주요 기능:**
- GitLab 웹훅을 수신하고 필요한 정보를 추출합니다.
- 로컬로 저장소를 클론하고 특정 커밋으로 체크아웃합니다.
- 수정된 파일 목록을 가져오고 파일 내용을 읽습니다.
- 코드 리뷰를 위한 프롬프트를 생성합니다.

**사전 조건 검사:**
- `LOCAL_REPO_PATH` 환경 변수가 설정되어 있어야 합니다.
- `ACCESS_TOKEN` 환경 변수가 설정되어 있어야 합니다 (퍼스널 액세스 토큰 또는 SSH 키 사용 시 필요).
- `PROEJCT_CONTEXT_PATH` 환경 변수가 설정되어 있어야 합니다 (gitlab reverse proxy).

**런타임 오류 검사:**
- `LOCAL_REPO_PATH`가 존재하지 않을 경우 `shutil.rmtree()`에서 예외가 발생할 수 있습니다.
- 추가된 파일 또는 수정 파일 디렉토리가 존재하지 않을 경우 `open()`에서 예외가 발생할 수 있습니다.

**optimization:**
```python
# gitlab_hook.py (optimized)
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from models import WebHookResponse, ErrorResponse, PromptCreateRequest
from dotenv import load_dotenv
import os
import git
from urllib.parse import urlparse
from pathlib import Path

load_dotenv()

LOCAL_REPO_PATH = Path(os.getenv("LOCAL_REPO_PATH"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PROJECT_CONTEXT_PATH = os.getenv("PROJECT_CONTEXT_PATH")

router = APIRouter(prefix="/gitlab")

@router.post("/hook/")
async def handle_gitlab_hook(request: Request):
    try:
        data = await request.json()
        repo_url = f"{PROJECT_CONTEXT_PATH}/{data['project']['path_with_namespace']}.git"

        repo = git.Repo.clone_repo(repo_url, LOCAL_REPO_PATH)
        repo.git.checkout(data["commit"]["id"])

        commit_id_list = [c["id"] for c in data["commits"]]
        title_dict = {c["id"]: c["title"] for c in data["commits"]}
        message_dict = {c["id"]: c["message"] for c in data["commits"]}

        added_files_content = {}
        modified_files_content = {}

        for commit in data["commits"]:
            for file_path in commit["added"]:
                absolute_file_path = LOCAL_REPO_PATH / file_path
                if absolute_file_path.is_file():
                    added_files_content[file_path] = absolute_file_path.read_text()

            for file_path in commit["modified"]:
                absolute_file_path = LOCAL_REPO_PATH / file_path
                if absolute_file_path.is_file():
                    modified_files_content[file_path] = absolute_file_path.read_text()

        request_data = PromptCreateRequest(
            id_list=commit_id_list,
            title_dict=title_dict,
            message_dict=message_dict,
            added_files_content=added_files_content,
            modified_files_content=modified_files_content
        )

        user_prompt = create_prompt(request_data)
        task = llm_code_review_task.apply_async(args=[user_prompt])

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(status_code=200, content={"detail": task.id})
```

**변경 사항:**
- `LOCAL_REPO_PATH`, `ACCESS_TOKEN`, `PROJECT_CONTEXT_PATH` 환경 변수를 로드하고 Path 객체로 변환합니다.
- `git.Repo.clone_repo()`를 사용하여 저장소를 클론하고 특정 커밋으로 체크아웃합니다.
- `commit["added"]`와 `commit["modified"]`에서 파일 경로를 처리할 때 `Path` 객체를 사용합니다.
- 예외 처리를 개선하고 FastAPI의 `HTTPException`을 사용합니다.

**주의 사항:**
- 이 코드는 GitLab 웹훅을 수신하는 데 중점을 둡니다. 코드 리뷰를 위한 프롬프트 생성 및 처리 로직은 별도의 함수로 추출되어야 합니다.
- 환경 변수에 따라 저장소 클론 위치가 변경될 수 있습니다. 적절한 보안 조치를 취해야 합니다.
- 이 애플리케이션은 GitLab 웹훅을 수신하기 위해 `/gitlab/hook/` 엔드포인트를 사용합니다. GitLab에서 해당 엔드포인트로 POST 요청을 보내야 합니다.