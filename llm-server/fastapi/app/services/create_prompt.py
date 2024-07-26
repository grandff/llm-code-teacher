from models import PromptCreateRequest

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