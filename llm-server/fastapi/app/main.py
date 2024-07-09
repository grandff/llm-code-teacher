from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from models import ErrorResponse
from dotenv import load_dotenv
import uvicorn
import os
from routers import ollama_run, celery_status

# .env 파일에서 환경 변수 로드
load_dotenv()

# fastapi
app = FastAPI()

# routers
app.include_router(ollama_run.router)
app.include_router(celery_status.router)

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


@app.middleware("https")
async def check_header_middleware(request: Request, call_next):
    headers = request.headers

    # Verify domain
    # TODO 도메인 정해지면 그때 바꾸기 + json으로 리턴
    # if "host" not in headers or headers["host"] not in ALLOWED_DOMAINS:
    #     raise HTTPException(status_code=403, detail="Domain not allowed")

    # Verify headers
    for key, value in REQUIRED_HEADERS.items():
        if key not in headers or headers[key] != value:
            error_response = ErrorResponse(detail="Invalid header")
            return JSONResponse(status_code=403, content=error_response.dict())

    response = await call_next(request)
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# uvicorn app.main:app --host 0.0.0.0 --port 8000