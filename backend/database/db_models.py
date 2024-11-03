from sqlalchemy import create_engine, Column, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from backend.config import config

Base = declarative_base()

class PdfEmbedding(Base):
    __tablename__ = "tb_embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_id = Column(Integer, autoincrement=True)
    filename = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(String, nullable=False)
    embedding = Column(Vector(1024), nullable=False)

    __table_args__ = (
        Index('idx_embedding', 'embedding', postgresql_using='ivfflat', postgresql_with={"lists": 100},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )

def create_db_and_table():
    engine = create_engine(config.database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
