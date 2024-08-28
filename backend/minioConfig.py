import os
from dotenv import load_dotenv
from minio import Minio
load_dotenv()


class MinioConfig:
    def __init__(self):
        self.env_state = os.getenv("ENV_STATE", "dev").upper()
        self.minio_access_key = os.getenv(f"{self.env_state}_MINIO_ACCESS_KEY")
        self.minio_secret_key = os.getenv(f"{self.env_state}_MINIO_SECRET_KEY")
        self.minio_bucket_name = os.getenv(f"{self.env_state}_MINIO_BUCKET_NAME")
        self.minio_endpoint = os.getenv(f"{self.env_state}_MINIO_ENDPOINT")


        if not all([self.minio_access_key, self.minio_secret_key, self.minio_bucket_name, self.minio_endpoint]):
            raise ValueError("One or more MinIO environment variables are not set. Please check your .env file.")

    def get_client(self):
        return Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False
        )



