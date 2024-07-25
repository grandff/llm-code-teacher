from celery import Celery
import os
from dotenv import load_dotenv
from ollama import Client
import time
import httpx
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

load_dotenv()

# 환경변수에서 브로커 URL을 설정합니다.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434")
celery_app = Celery('worker', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# langchain을 사용해서 코드 리뷰 작성
@celery_app.task(name="tasks.llm_code_review_task_by_langchain")
def llm_code_review_task_by_langchain(prompt) :
    try:
        # llm 생성
        llm = ChatOllama(           
            base_url = "http://host.docker.internal:11434",
            model="llama3.1",
            temperature=0,
        )        
        
        # prompt 생성
        code_review_messages = ChatPromptTemplate.from_messages([
            ("system", """        
            You are an expert software engineer specializing in code review and software quality analysis. You will receive the commit message, title, full content of added files, and full content of modified files, all provided in code block format.

            Your task is to perform a detailed analysis of the changes, including the following aspects:
            1. **Analysis Summary:** Summarize the main changes of the commit in one or two sentences.
            2. **Key Features:** Describe the key features of the added or modified files.
            3. **Pre-condition Check:** Verify if functions or methods have the necessary preconditions, such as correct variable states or value ranges.
            4. **Runtime Error Check:** Identify any code that may potentially cause runtime errors and check for other potential risks.
            5. **Optimization:** Inspect for optimization points in the code patches and recommend optimized code if performance issues are found.
            6. **Security Issue:** Check if the code uses any modules with severe security flaws or includes any security vulnerabilities.
            7. **Evaluation:** Provide an overall assessment of the code quality, functionality, and maintainability.
            
            The recommended code format for the Optimization step should look like this

            ---
            ```python
            # Before optimization
            for i in range(len(data)):
                process(data[i])
            
            # After optimization
            for item in data:
                process(item)
            ```
            ---

            The code you use in a code block should only be written in the development language used by the developer.

            Focus on providing constructive feedback to enhance code quality, maintainability, and performance.
            """),
            ("user", "{prompt}")
        ])
        formatting_messages = ChatPromptTemplate.from_messages([
            ("system", """
            You are an experienced technical writer skilled in documenting and formatting code reviews. Your task is to take the results from a code review and format them into a markdown file. The markdown file must be written in English and should include the following sections: Analysis Summary, Key Features, Pre-condition Check, Runtime Error Check, Optimization, Security Issue, and Evaluation. Each section should be formatted appropriately:

            - **Analysis Summary:** Summarize the code review findings in one or two lines.
            - Key Features:** Analyze and describe the key features of the added or modified files.
            - Precondition checks:** Checks that a function or method has the necessary variable states or ranges of values to function correctly.
            - Runtime error checking:** Examines code for possible runtime errors and identifies other potential risks.
            - Optimization:** Scans code patches for optimization points and recommends optimized code if performance is deemed poor.
            - Security issues:** Scans your code to see if it uses modules with serious security flaws or contains security vulnerabilities.
            - Evaluation:** Comprehensively evaluates your work. Consider the quality, functionality, and maintainability of the code.
            
            Example Markdown Ouput is as follows:
            ---
            # 코드 리뷰 결과

            ## 분석 요약
            이 커밋은 새로운 기능 추가와 기존 코드 수정이 포함되어 있습니다.

            ## 주요 특징
            - 새로운 파일: `new_feature.py` - 새로운 기능을 구현한 파일입니다.
            - 수정된 파일: `existing_module.py` - 기존 모듈에 기능을 추가하고 버그를 수정하였습니다.

            ## 사전 조건 검사
            - 함수 `calculate`가 입력값으로 0 이하의 값을 받지 않도록 검사해야 합니다.

            ## 런타임 오류 검사
            - `new_feature.py`의 `open_file` 함수에서 파일이 존재하지 않을 경우 발생할 수 있는 오류를 처리해야 합니다.

            ## 최적화
            - `existing_module.py`의 루프 구조를 최적화하여 성능을 개선할 수 있습니다.
            ```python
            # Before optimization
            for i in range(len(data)):
                process(data[i])
            
            # After optimization
            for item in data:
                process(item)
            
            ## 보안 문제
            - 외부 입력을 처리할 때 SQL 인젝션 공격에 취약한 부분이 있습니다. 이를 방지하기 위한 입력 검증이 필요합니다.
            
            ## 평가
            - 전반적으로 코드의 기능성은 향상되었으나, 몇 가지 최적화 및 보안 개선이 필요합니다. 유지보수성을 위해 주석을 추가하는 것도 좋습니다.
            ---

            Ensure the markdown document is clear, well-structured, and easy to read. Remember, the entire document must be written in Korean.
            """),
            ("user", "{review_result}")
        ])
        
        # chain 생성
        # 1. 코드 분석 실행. 어떤 코드고, 리팩토링하면 좋은 것 까지.
        review_chain = code_review_messages | llm
        # 2. 해당 코드 분석을 포멧에 맞게 변환.
        formatting_chain = formatting_messages | llm
        
        # 체인 실행
        final_chain = {"review_result" : review_chain} | formatting_chain
            
        # 데이터 리턴
        result = final_chain.invoke({
            "prompt" : prompt
        })
        
        # 파일 생성
        file_dir = "/home/example/"
        file_name = "example_langchain.md"
        file_info = save_md_to_file(result.content, file_dir, file_name)
        
        # 1초 딜레이
        time.sleep(1)
        
        return { "response" : result.content, "info" : file_info}        
    except Exception as e :
        return str(e)


# 단일 프롬프트로 코드 리뷰 작성 
@celery_app.task(name="tasks.llm_code_review_task")
def llm_code_review_task(prompt):    
    try:
        client = Client(host=OLLAMA_URL)
        response = client.chat(
            model='llama3', 
            options={
                'temperature': 0.1,
            },
            messages=[
                {
                    'role' : 'system',
                    'content' : get_code_review_prompot,         
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
        
        # 1초 딜레이
        time.sleep(1)
        
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

# single prompt
def get_code_review_prompot() :
    return """
    You are an expert software engineer specializing in code review and software quality analysis. You will receive the commit message, title, full content of added files, and full content of modified files, all provided in code block format.

    Your task is to perform a detailed analysis of the changes, including the following aspects:
    1. **Analysis Summary:** Summarize the main changes of the commit in one or two sentences.
    2. **Key Features:** Describe the key features of the added or modified files.
    3. **Pre-condition Check:** Verify if functions or methods have the necessary preconditions, such as correct variable states or value ranges.
    4. **Runtime Error Check:** Identify any code that may potentially cause runtime errors and check for other potential risks.
    5. **Optimization:** Inspect for optimization points in the code patches and recommend optimized code if performance issues are found.
    6. **Security Issue:** Check if the code uses any modules with severe security flaws or includes any security vulnerabilities.
    7. **Evaluation:** Provide an overall assessment of the code quality, functionality, and maintainability.
    
    The recommended code format for the Optimization step should look like this

    Ensure that your feedback is constructive, aiming to enhance code quality, maintainability, and performance. The final markdown document must be clear, well-structured, and easy to read.
    The code you use in a code block should only be written in the development language used by the developer.
    Focus on providing constructive feedback to enhance code quality, maintainability, and performance.
    
    Example Markdown Ouput is as follows:
    ---
    # 코드 리뷰 결과

    ## 분석 요약
    이 커밋은 새로운 기능 추가와 기존 코드 수정이 포함되어 있습니다.

    ## 주요 특징
    - 새로운 파일: `new_feature.py` - 새로운 기능을 구현한 파일입니다.
    - 수정된 파일: `existing_module.py` - 기존 모듈에 기능을 추가하고 버그를 수정하였습니다.

    ## 사전 조건 검사
    - 함수 `calculate`가 입력값으로 0 이하의 값을 받지 않도록 검사해야 합니다.

    ## 런타임 오류 검사
    - `new_feature.py`의 `open_file` 함수에서 파일이 존재하지 않을 경우 발생할 수 있는 오류를 처리해야 합니다.

    ## 최적화
    - `existing_module.py`의 루프 구조를 최적화하여 성능을 개선할 수 있습니다.
    ```python
    # Before optimization
    for i in range(len(data)):
        process(data[i])
    
    # After optimization
    for item in data:
        process(item)
        
    ## 보안 문제
    - 외부 입력을 처리할 때 SQL 인젝션 공격에 취약한 부분이 있습니다. 이를 방지하기 위한 입력 검증이 필요합니다.
    
    ## 평가
    - 전반적으로 코드의 기능성은 향상되었으나, 몇 가지 최적화 및 보안 개선이 필요합니다. 유지보수성을 위해 주석을 추가하는 것도 좋습니다.
    
    ---
    """       
    