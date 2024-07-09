from celery import Celery
import os
from dotenv import load_dotenv
from ollama import Client
import httpx

load_dotenv()

# 환경변수에서 브로커 URL을 설정합니다.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

celery_app = Celery('worker', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(name="tasks.llm_code_review_task")
def llm_code_review_task(prompt):    
    try:
        client = Client(host=OLLAMA_URL)
        response = client.chat(
            model='llama3', 
            messages=[
                {
                    'role' : 'system',
                    'content' : """
                    You're a very good software analyst and engineer. 
                    From now on, the user is going to show you a complete set of committed source code. 
                    You're going to look at it, analyze it, and tell us what you find. 
                    Please provide your analysis in markdown format.                     
                    Analyze the source code, predict the outcome of a hypothetical execution, and present a refactoring of the source code to improve performance or make it more readable.
                    
                    Please set the title of each item to match the markdown format (ex: use ##)
                    
                    All responses must be in Korean."""
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])                 
        ai_response = response['message']['content']
        return ai_response
    except httpx.HTTPStatusError as exc:
        return str(exc)