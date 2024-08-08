from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from models import ErrorResponse
from dotenv import load_dotenv
import uvicorn
import os
from routers import ollama_run, celery_status, gitlab_hook

# .env 파일에서 환경 변수 로드
load_dotenv()

# fastapi
app = FastAPI()

# routers
app.include_router(ollama_run.router)
app.include_router(celery_status.router)
app.include_router(gitlab_hook.router)

ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "").split(",")
REQUIRED_HEADERS = {"API-Key": os.getenv("API_KEY")}

# HTTP Basic 인증 설정
# 사용자 이름과 비밀번호를 이용해서 인증
security = HTTPBasic()

# 인증 함수
# Httpbasiccredentials를 종속성으로 받아옴
def docs_auth(credentials: HTTPBasicCredentials = Depends(security)) :
    correct_username = os.getenv("DOCS_USERNAME")
    correct_password = os.getenv("DOCS_PASSWORD")
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.middleware("http")
async def check_header_middleware(request: Request, call_next):
    headers = request.headers
    
    # /docs 및 /openapi.json 경로에 대한 예외 처리
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
        response = await call_next(request)
        return response

    # Verify domain    
    # if "host" not in headers or headers["host"] not in ALLOWED_DOMAINS:
            # error_response = ErrorResponse(detail="Invalid header")
            # return JSONResponse(status_code=403, content=error_response.dict())
    #     raise HTTPException(status_code=403, detail="Domain not allowed")    
    
    # Verify headers    
    for key, value in REQUIRED_HEADERS.items():        
        if key not in headers or headers[key] != value:
            error_response = ErrorResponse(detail="Invalid header")
            return JSONResponse(status_code=403, content=error_response.dict())

    response = await call_next(request)
    return response

@app.get("/")
async def root_get_check():
    return {"status": "root_get_ok"}

@app.post("/")
async def root_post_check():
    return {"status": "root_post_ok"}

@app.get("/health")
async def health_get_check():
    return {"status": "ok"}

@app.post("/health")
async def health_post_check():
    return {"status": "ok"}

@app.post("/fileserver")
async def fileserver_post_check():
    return {"status": "fileserver post ok"}

@app.get("/fileserver")
async def fileserver_get_check():
    return {"status": "fileserver get ok"}


@app.post("/webhook")
async def webhook_post_check():
    return {"status": "webhook post ok"}


@app.get("/webhook")
async def webhook_get_check():
    return {"status": "webhook get ok"}

# swagger ui endpoint
# 자동생성된 api 문서에 포함 안되도록 하기 위해 include false 옵션 부여
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(credentials: HTTPBasicCredentials = Depends(docs_auth)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

# OpenAPI 스키마 엔드포인트
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(credentials: HTTPBasicCredentials = Depends(docs_auth)):
    return JSONResponse(get_openapi(title="docs", version="1.0.0", routes=app.routes))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# uvicorn app.main:app --host 0.0.0.0 --port 8000