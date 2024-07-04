from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from app.models import PromptRequest, ErrorResponse
from dotenv import load_dotenv
import httpx
import os
from ollama import AsyncClient, Client
import asyncio

# .env 파일에서 환경 변수 로드
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "")

router = APIRouter()

@router.post("/code/review")
async def llm_code_review(request : PromptRequest):    
    try:        
        client = Client(host=OLLAMA_URL)
        response = client.chat(
            model='llama3', 
            messages=[
                {
                    'role' : 'system',
                    'content' : "You're a very good software analyst and engineer. From now on, the user is going to show you a complete set of committed source code. You're going to look at it, analyze it, and tell us what you find. Please provide your analysis in markdown format. All responses must be in Korean."
                },
                {
                    'role': 'user',
                    'content': request.prompt,
                },
            ])         
        print(response)
        ai_response = response['message']['content']
        return ai_response
    except httpx.HTTPStatusError as exc:
        error_response = ErrorResponse(detail=exc.response.text)
        return JSONResponse(status_code=403, content=error_response.dict())
            