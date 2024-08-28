import psycopg2
from psycopg2 import sql
from backend.config import config
from dotenv import load_dotenv


async def connect_to_db():
    load_dotenv()

    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        host=config.POSTGRES_URL,
        port=5432
    )

    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='vector');")
    exists = cur.fetchone()[0]

    if not exists:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
    cur.close()

    return conn
