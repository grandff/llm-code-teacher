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
        file_dir = "/home/example/"
        file_name = "example.md"
        file_info = save_md_to_file(ai_response, file_dir, file_name)
        
        return { "response" : ai_response, "info" : file_info}
    except httpx.HTTPStatusError as exc:
        return str(exc)
    

# markdown 파일 생성
def save_md_to_file(markdown_str : str, directory : str, file_name : str) :
    # 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(directory):
        os.makedirs(directory)
        
     # 파일 경로 생성
    file_path = os.path.join(directory, file_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_str)
    
    # 파일 객체 정보 변환
    file_info = {
        'file_path' : file_path,
        'file_name' : os.path.getsize(file_path)
    }
    
    return file_info