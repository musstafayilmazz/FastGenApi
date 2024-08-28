from pydantic import BaseModel

class FilenameAndQuestionRequest(BaseModel):
    filename: str
    query: str