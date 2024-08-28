from fastapi import APIRouter, HTTPException
from backend.models.delete_file_model import FilenameRequest
from backend.services.fileService import delete_pdf_and_records
from backend.services.minioClientService import list_files as minio_list_files

router = APIRouter(
    prefix="/file",
    tags=["File"]
)


@router.delete("/delete")
async def delete_pdf_and_records_route(request: FilenameRequest):
    """
    This route deletes a given file from MinIO storage and PostgreSQL database.

    Parameters:
    - request: An object containing the name of the file.
    """
    try:
        result = delete_pdf_and_records(request.filename)

        if result["status"] == "success":
            return {"status": "success", "message": result["message"]}
        else:

            raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException as e:

        raise e

    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_files():
    """
    This route bring all downloaded file from minio

    - return: List of all downloaded files
    """
    return minio_list_files()



