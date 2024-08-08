from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    
class PromptRequest(BaseModel):
    prompt: str
    
class WebHookResponse(BaseModel) :    
    error : str
    added : dict
    modified : dict

class PromptCreateRequest(BaseModel) :
    id_list : list
    title_dict : dict
    message_dict : dict    
    added_files_content : dict
    modified_files_content : dict

class PromptCreateRequestV1(BaseModel) :
    file_ext : str
    file_name : str
    file_data : str