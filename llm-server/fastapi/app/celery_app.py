import time
import logging
from celery import Celery
import os
from dotenv import load_dotenv
import httpx
import requests
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

load_dotenv()

# 환경변수에서 브로커 URL을 설정합니다.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
FILE_UPLOAD_URL= os.getenv("FILE_UPLOAD_URL", "") 
celery_app = Celery('worker', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# llm 생성
llama_llm = ChatOllama(           
    base_url = OLLAMA_URL,
    model="llama3.1",
    temperature=0,
)     
mistral_llm = ChatOllama(
    base_url = OLLAMA_URL,
    model="mistral",
    temperature=0,
)     

# prompt 생성
code_review_messages = ChatPromptTemplate.from_messages([
    ("system", """
    You're a very good software analyst. From now on, users will show you the entire committed source code. Take a look at it, analyze it, and tell us what you find. 
    After looking at the source code, present an optimized version of the code, including performance improvements. 

    As you analyze the source code, keep the following topics in mind as you do so
    - Analysis summary: Summarize your code review findings in one or two lines.
    - Key features: Analyze and describe the key features of each file.
    - Prerequisite checks: Verify that the function or method has the necessary variable states or value ranges to function correctly.
    - Runtime error checking: Inspect your code for possible runtime errors and identify other potential risks.
    - Optimization: Scans code patches for optimization points and recommends optimized code if it appears to be degrading performance. 
    - Security issues: Scan your code to see if it uses modules with serious security flaws or contains security vulnerabilities.
    - Evaluation: Evaluate your work comprehensively. Considers the quality, functionality, and maintainability of the code.

    Return a response in markdown so that your analysis is easy to parse.
    The topics above are the same as the subheadings in your final analysis. In particular, be sure to write the entire code in the form of code blocks in Markdown for optimizations.
    The Markdown documentation must be written in Korean.
    Do not write any additional text other than the response values in Markdown format.
    """),
    ("human", "{prompt}")
])
translate_messages = ChatPromptTemplate.from_messages([
    ("system", """
    You are an excellent translator. Please translate the markdown written by the user into Korean. 
    At this time, for the content in the code block, only the annotation should be translated, and the code should be left as it is.
    """),
    ("human", "{review_result}")
])

# new version
@celery_app.task(name="tasks.llm_code_review_task")
def llm_code_review_task(prompt, user_name) :
    # 1.5초 딜레이
    time.sleep(1.5)    
    try:
        # chain 생성
        # 1. 코드 분석 실행. 어떤 코드고, 리팩토링하면 좋은 것 까지.
        review_chain = code_review_messages | llama_llm
        # 2. 해당 코드 분석을 포멧에 맞게 변환.
        translate_chain = translate_messages | mistral_llm
        # 체인 실행
        final_chain = {"review_result" : review_chain} | translate_chain
        
        # 데이터 리턴
        result = final_chain.invoke({
            "prompt" : prompt
        })
        print(result)
        logging.info("end of lang chain")
        ai_response = result.content        
        # 현재 시간 기준으로 파일명 생성
        now = datetime.now()    
        # 원하는 형식으로 날짜와 시간 포맷팅   
        logging.info("start save md file")     
        formatted_date = now.strftime("%Y%m%d_%H%M%S")        
        file_dir = f"/home/report/{user_name}/"  
        file_name = f"report_{formatted_date}.md"
        file_info = save_md_to_file(ai_response, file_dir, file_name)
        logging.info("end save md file")     
        
        # 파일서버로 전송하기
        logging.info("start send to file server")
        file_send_response = send_to_file_server(file_info, user_name)
        logging.info("end send to file server")
        logging.info(file_send_response)
        try :                
            logging.info(file_send_response.json())
            file_response = file_send_response.json()
        except Exception as e :
            logging.error(e)
            file_response = file_send_response
        
        return { "response" : ai_response, "file_info" : file_info, "file_response" : ""}
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

# 파일서버로 보고서 파일 전송
def send_to_file_server(file_info : dict, user_name : str) :    
    # 파일 경로    
    files = {'file': open(file_info['file_path'], 'rb')}
    # palyload
    body = {
        "username" : user_name,        
    }
    response = requests.post(FILE_UPLOAD_URL, files=files, data=body)
    
    # 파일 객체 닫기
    files['file'].close()
    
    return response