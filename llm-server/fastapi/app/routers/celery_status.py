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

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'status': 'Pending...'
        }
    elif task_result.state != 'FAILURE':
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'result': task_result.result
        }
    else:
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'status': str(task_result.info)  
        }
    return response
