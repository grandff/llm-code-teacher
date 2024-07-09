from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    
class PromptRequest(BaseModel):
    prompt: str