from pydantic import BaseModel

class PdfAndQuestionRequest(BaseModel):
    URL: str
    minio_file_name: str
    query: str