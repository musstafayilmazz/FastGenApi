import os
import logging
import fitz  # PyMuPDF
from backend.pretrainedModels.bge3_embedding import SingletonModel
import torch
from sqlalchemy import func
from backend.database.db_models import create_db_and_table, PdfEmbedding
from fastapi import HTTPException
import gc


def generate_embedding(text):
    """Generate embeddings for a given text using singleton model."""
    model_instance = SingletonModel()
    tokenizer = model_instance.tokenizer
    model = model_instance.model

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(model.device)

    with torch.no_grad():
        outputs = model(**inputs)

    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

    # Clean up tensors to free GPU memory
    del inputs, outputs
    torch.cuda.empty_cache()
    gc.collect()

    return embeddings.tolist()


def process_pdf_chunks(pdf_path, minio_file_name, batch_size=10):
    logging.info(f"Starting PDF processing for {pdf_path}")

    doc = fitz.open(pdf_path)
    chunks = []

    chunk_size = 100
    total_words = 0

    # Efficiently extract text from PDF and split into chunks
    for page in doc:
        words = page.get_text().split()
        total_words += len(words)
        chunks.extend([" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)])

    # Handle case where PDF does not contain enough words
    if total_words < chunk_size:
        os.remove(pdf_path)
        logging.warning(f"PDF {minio_file_name} does not contain enough words to create a chunk.")
        raise ValueError(f"PDF {minio_file_name} does not contain enough words to create a chunk.")

    # Setup database session
    session = create_db_and_table()
    latest_pdf_id = session.query(func.max(PdfEmbedding.pdf_id)).scalar() or 0
    new_pdf_id = latest_pdf_id + 1
    logging.info(f"Processing chunks for PDF {minio_file_name} with new PDF ID {new_pdf_id}")

    # Process and store embeddings in batches
    all_pdf_embeddings = []
    for idx, chunk in enumerate(chunks):
        try:
            embeddings = generate_embedding(chunk)
            pdf_embedding = PdfEmbedding(
                pdf_id=new_pdf_id,
                filename=minio_file_name,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embeddings
            )
            all_pdf_embeddings.append(pdf_embedding)

            if (idx + 1) % batch_size == 0:
                session.bulk_save_objects(all_pdf_embeddings)
                session.commit()
                all_pdf_embeddings.clear()

        except Exception as exc:
            logging.error(f"Chunk {idx} generated an exception: {exc}")

    # Final commit for remaining chunks
    if all_pdf_embeddings:
        session.bulk_save_objects(all_pdf_embeddings)
        session.commit()

    session.close()
    logging.info(f"Successfully processed and indexed PDF {minio_file_name} into PostgreSQL with pdf_id {new_pdf_id}")
    os.remove(pdf_path)
    logging.info(f"Deleted temporary PDF file {pdf_path}")

    # Clean up
    del chunks, all_pdf_embeddings
    torch.cuda.empty_cache()
    gc.collect()

    # Unload model to free memory
    unload_model()


def unload_model():
    """Unload the model from memory to free up resources."""
    model_instance = SingletonModel()
    if model_instance.model:
        del model_instance.model
    if model_instance.tokenizer:
        del model_instance.tokenizer
    SingletonModel._instance = None

    torch.cuda.empty_cache()
    gc.collect()


def get_related_chunks(question):
    logging.info(f"Generating embedding for question: {question}")
    question_embedding = generate_embedding(question)

    session = create_db_and_table()
    latest_pdf_id = session.query(func.max(PdfEmbedding.pdf_id)).scalar()

    try:
        query = session.query(PdfEmbedding.chunk_text).filter(
            PdfEmbedding.pdf_id == latest_pdf_id
        ).order_by(
            func.l2_distance(PdfEmbedding.embedding, func.cast(question_embedding, PdfEmbedding.embedding.type))
        ).limit(5)

        result = query.all()
        related_chunks = [row.chunk_text for row in result]
        logging.info(f"Retrieved {len(related_chunks)} related chunks for the question.")
    finally:
        session.close()

    # Clean up
    del question_embedding
    torch.cuda.empty_cache()
    gc.collect()

    return related_chunks


def get_related_chunks_by_filename(query, filename):
    logging.info(f"Generating embedding for question: {query}")
    question_embedding = generate_embedding(query)

    session = create_db_and_table()
    file_exists = session.query(PdfEmbedding).filter(PdfEmbedding.filename == filename).first()
    if not file_exists:
        raise HTTPException(status_code=404, detail=f"No records found for filename: {filename}")

    try:
        query = session.query(PdfEmbedding.chunk_text).filter(
            PdfEmbedding.filename == filename
        ).order_by(
            func.l2_distance(PdfEmbedding.embedding, func.cast(question_embedding, PdfEmbedding.embedding.type))
        ).limit(5)

        result = query.all()
        related_chunks = [row.chunk_text for row in result]
        logging.info(f"Retrieved {len(related_chunks)} related chunks for filename {filename}.")
    finally:
        session.close()

    # Clean up
    del question_embedding
    torch.cuda.empty_cache()
    gc.collect()

    return related_chunks
