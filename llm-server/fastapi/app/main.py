from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
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


@app.middleware("http")
async def check_header_middleware(request: Request, call_next):
    headers = request.headers

    # Verify domain
    # TODO 도메인 정해지면 그때 바꾸기 + json으로 리턴
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# uvicorn app.main:app --host 0.0.0.0 --port 8000