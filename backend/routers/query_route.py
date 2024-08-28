from fastapi import APIRouter, HTTPException
from backend.models.pdf_by_filename_model import FilenameAndQuestionRequest
from backend.models.pdf_and_question_model import PdfAndQuestionRequest
from backend.services.queryService import get_related_chunks_by_filename
from backend.services.queryService import get_related_chunks
from backend.services.minioClientService import upload_file
from backend.services.queryService import process_pdf_chunks

router = APIRouter(
    prefix="/pdf-query",
    tags=["PDF Query"],
)



@router.post("/from-name/")
async def query_pdf_by_filename(request: FilenameAndQuestionRequest):
    """
        Query PDF by Filename.

        This endpoint retrieves the most related chunks of text from a PDF stored in the database,
        based on a given filename and a query. The PDF is identified by its filename, and the
        provided query is used to search for and rank the related text chunks within the PDF.

        :param request: An instance of FilenameAndQuestionRequest containing the following fields:
            - filename (str): The name of the PDF file stored in the database.
            - query (str): The query string used to find related text chunks in the PDF.

        :return: A dictionary containing:
            - status (str): The status of the operation ('success' if successful).
            - related_chunks (List[str]): A list of the most related text chunks from the PDF.
        :raises HTTPException: If an error occurs during processing, an HTTP 500 error is raised with the error details.
        """
    try:

        related_chunks = get_related_chunks_by_filename(request.query, request.filename)

        return {
            "status": "success",
            "related_chunks": related_chunks
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-url/")
async def process_and_query_pdf(request: PdfAndQuestionRequest):
    """
        Process and Query PDF from URL.

        This endpoint downloads a PDF from the provided URL, processes it by extracting text chunks,
        uploads the PDF to MinIO, and then queries the most related chunks based on the provided query.

        :param request: An instance of PdfAndQuestionRequest containing the following fields:
            - URL (str): The URL of the PDF to download.
            - minio_file_name (str): The name to use when storing the PDF in MinIO.
            - query (str): The query string used to find related text chunks in the PDF.

        :return: A dictionary containing:
            - status (str): The status of the operation ('success' if successful).
            - message (str): A message indicating the successful processing and uploading of the PDF.
            - related_chunks (List[str]): A list of the most related text chunks from the processed PDF.
        :raises HTTPException: If an error occurs during processing, an HTTP 500 error is raised with the error details.
        """
    pdf_path = "/tmp/temp_pdf.pdf"
    try:
        upload_file(request.URL, request.minio_file_name)
        process_pdf_chunks(pdf_path, request.minio_file_name)
        related_chunks = get_related_chunks(request.query)

        return {
            "status": "success",
            "message": f"PDF processed and uploaded with name {request.minio_file_name}",
            "related_chunks": related_chunks
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
