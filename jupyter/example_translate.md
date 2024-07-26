**분석 요약:** 
GitLab 웹훅을 처리하고 코드 리뷰를 위한 프롬프트를 생성하는 FastAPI 애플리케이션입니다. 로컬로 저장소를 클론하고 커밋 내용을 읽어 프롬프트에 추가합니다.

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