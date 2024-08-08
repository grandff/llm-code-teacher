from models import PromptCreateRequest, PromptCreateRequestV1

# user prompt 생성 v1 
def create_prompt_v1(request : PromptCreateRequestV1) :
    prompt = f"""
    You are an experienced technical writer skilled in documenting and formatting code reviews. 
    Your task is to take the results from a code review and format them into a markdown file. 
    The markdown file must be written in English and should include the following sections: Analysis Summary, Key Features, Pre-condition Check, Runtime Error Check, Optimization, Security Issue, and Evaluation. 
    Each section should be formatted appropriately:

    - **Analysis Summary:** Summarize the code review findings in one or two lines.
    - **Key Features:** Analyze and describe the key features of the added or modified files.
    - **Precondition checks:** Checks that a function or method has the necessary variable states or ranges of values to function correctly.
    - **Runtime error checking:** Examines code for possible runtime errors and identifies other potential risks.
    - **Optimization:** Scan your code and recommend optimized code. When recommending code, be sure to include the full source of the file. Please write your code using code blocks to conform to the markdown format - this is a must. 
    - **Security issues:** Scans your code to see if it uses modules with serious security flaws or contains security vulnerabilities.
    - **Evaluation:** Comprehensively evaluates your work. Consider the quality, functionality, and maintainability of the code.
                
    Ensure the markdown document is clear, well-structured, and easy to read.
    
    ```{request.file_ext}
    # {request.file_name}
    {request.file_data}
    ```
    """
    return prompt
    
# user prompt 생성
def create_prompt(request : PromptCreateRequest) :
    id_list = request.id_list
    # 추가된 id가 없으면 안됨
    if len(id_list) == 0 :
        return ""
    
    commit_id = id_list[0]
    
    title = request.title_dict[commit_id]
    message = request.message_dict[commit_id]    
    added_files_content = request.added_files_content
    modified_files_content = request.modified_files_content
    
    # prompt 생성
    prompt = f"""
    Below is a list of what I've been working on. 

    ---
    Commit Title: {title}
    Commit Message : {message}
    File List : 
    """
    
    for key, value in added_files_content.items() :
        prompt += f"""
        ```python
        # {key}
        {value}
        ```
        """
        
    for key, value in modified_files_content.items() :
        prompt += f"""
        ```python
        # {key}
        {value}
        ```
        """
    
    
    return prompt