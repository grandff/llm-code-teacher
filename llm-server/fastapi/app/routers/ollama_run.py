from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from models import PromptRequest, ErrorResponse
from dotenv import load_dotenv
from celery.result import AsyncResult
import httpx
import os
from ollama import AsyncClient, Client
import asyncio
from celery_app import celery_app, llm_code_review_task

# .env 파일에서 환경 변수 로드
load_dotenv()

router = APIRouter()

@router.post("/code/review")
async def llm_code_review(request : PromptRequest):        
    task = llm_code_review_task.apply_async(args=[request.prompt])
    return {"task_id": task.id}
            