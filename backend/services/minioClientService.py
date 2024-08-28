from backend.minioConfig import MinioConfig
from fastapi import HTTPException
import logging
import requests
from minio import Minio
from minio.error import S3Error
import os

def list_files():
    """
    Lists all files in the configured MinIO bucket.

    :return: A dictionary with a list of filenames in the bucket.
    :raises HTTPException: If there is an error accessing the MinIO bucket.
    """
    try:
        logging.info("Initializing MinIO client configuration.")
        config = MinioConfig()
        minio_client = config.get_client()

        logging.info(f"Listing files in bucket: {config.minio_bucket_name}")
        objects = minio_client.list_objects(config.minio_bucket_name)
        file_list = [obj.object_name for obj in objects]

        logging.info(f"Retrieved {len(file_list)} files from the bucket.")
        return {"files": file_list}

    except Exception as e:
        logging.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

def upload_file(URL, minio_file_name):
    try:
        response = requests.get(URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading the PDF: {e}")

    pdf_path = "/tmp/temp_pdf.pdf"
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(response.content)

    config = MinioConfig()
    minio_client = Minio(
        config.minio_endpoint,
        access_key=config.minio_access_key,
        secret_key=config.minio_secret_key,
        secure=False
    )

    try:
        if not minio_client.bucket_exists(config.minio_bucket_name):
            minio_client.make_bucket(config.minio_bucket_name)
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Error creating bucket: {e}")

    try:
        minio_client.fput_object(
            bucket_name=config.minio_bucket_name,
            object_name=minio_file_name,
            file_path=pdf_path,
            content_type='application/pdf'
        )
        print(f"Successfully uploaded {minio_file_name} to MinIO bucket {config.minio_bucket_name}")

    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Error uploading the PDF to MinIO: {e}")

