from pydantic import BaseModel

class FilenameRequest(BaseModel):
    filename: str