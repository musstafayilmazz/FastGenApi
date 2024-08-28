from minio import Minio
from minio.error import S3Error
from sqlalchemy import delete
from backend.config import config
from backend.database.db_models import create_db_and_table, PdfEmbedding
from fastapi import HTTPException

def delete_pdf_and_records(filename):
    minio_client = Minio(
        config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=False
    )

    try:
        minio_client.remove_object(config.MINIO_BUCKET_NAME, filename)
        print(f"Successfully deleted {filename} from MinIO bucket {config.MINIO_BUCKET_NAME}")
    except S3Error as e:
        print(f"Error deleting the file from MinIO: {e}")
        return {"status": "error", "message": f"Failed to delete {filename} from MinIO"}

    session = create_db_and_table()

    try:

        deleted_rows = session.query(PdfEmbedding).filter(PdfEmbedding.filename == filename).delete()

        if deleted_rows == 0:

            raise HTTPException(status_code=404, detail=f"No records found for filename {filename}")

        session.commit()
        print(f"Successfully deleted records with filename {filename} from PostgreSQL")
        return {"status": "success", "message": f"Deleted {filename} from MinIO and PostgreSQL"}

    except HTTPException as http_exc:

        raise http_exc

    except Exception as e:

        print(f"Error deleting records from PostgreSQL: {e}")
        session.rollback()
        return {"status": "error", "message": f"Failed to delete records for {filename} from PostgreSQL"}
