import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from unittest.mock import patch, MagicMock, mock_open
import pytest

from backend.services.queryService import (
    generate_embedding,
    process_pdf_chunks,
    get_related_chunks,
    get_related_chunks_by_filename,
    unload_model
)

from fastapi import HTTPException

@patch('backend.services.queryService.SingletonModel')
def test_generate_embedding_success(mock_singleton_model):
    text = "This is a test sentence."

    mock_tokenizer = MagicMock()
    mock_model = MagicMock()

    mock_singleton_instance = MagicMock()
    mock_singleton_instance.tokenizer = mock_tokenizer
    mock_singleton_instance.model = mock_model
    mock_singleton_model.return_value = mock_singleton_instance

    mock_inputs = MagicMock()
    mock_tokenizer.return_value = mock_inputs

    mock_outputs = MagicMock()
    mock_last_hidden_state = MagicMock()
    mock_outputs.last_hidden_state = mock_last_hidden_state

    mock_last_hidden_state.mean.return_value.squeeze.return_value.cpu.return_value.numpy.return_value.tolist.return_value = [0.1, 0.2, 0.3]

    mock_model.return_value = mock_outputs

    embeddings = generate_embedding(text)

    assert embeddings == [0.1, 0.2, 0.3]
    mock_tokenizer.assert_called_with(text, return_tensors="pt", truncation=True, padding=True)
    mock_model.assert_called_once_with(**mock_inputs)

@patch('backend.services.queryService.SingletonModel')
def test_generate_embedding_exception(mock_singleton_model):

    text = "This is a test sentence."

    mock_singleton_model.side_effect = Exception("Model loading error")

    with pytest.raises(Exception) as exc_info:
        generate_embedding(text)

    assert "Model loading error" in str(exc_info.value)

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
@patch('backend.services.queryService.fitz.open')
def test_process_pdf_chunks_success(mock_fitz_open, mock_create_db_and_table, mock_generate_embedding):
    pdf_path = '/path/to/test.pdf'
    minio_file_name = 'test.pdf'
    batch_size = 2

    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Word " * 200
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    mock_generate_embedding.return_value = [0.1, 0.2, 0.3]

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session
    mock_session.query.return_value.scalar.return_value = 1

    with patch('os.remove') as mock_os_remove:
        process_pdf_chunks(pdf_path, minio_file_name, batch_size)

    mock_fitz_open.assert_called_with(pdf_path)
    assert mock_generate_embedding.call_count > 0
    mock_session.bulk_save_objects.assert_called()
    mock_session.commit.assert_called()
    mock_session.close.assert_called()
    mock_os_remove.assert_called_with(pdf_path)

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
@patch('backend.services.queryService.fitz.open')
def test_process_pdf_chunks_not_enough_words(mock_fitz_open, mock_create_db_and_table, mock_generate_embedding):
    pdf_path = '/path/to/test.pdf'
    minio_file_name = 'test.pdf'

    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Word " * 50
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    with patch('os.remove') as mock_os_remove:
        with pytest.raises(ValueError) as exc_info:
            process_pdf_chunks(pdf_path, minio_file_name)

    assert f"PDF {minio_file_name} does not contain enough words to create a chunk." in str(exc_info.value)
    mock_os_remove.assert_called_with(pdf_path)

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
@patch('backend.services.queryService.fitz.open')
def test_process_pdf_chunks_chunk_exception(mock_fitz_open, mock_create_db_and_table, mock_generate_embedding):
    pdf_path = '/path/to/test.pdf'
    minio_file_name = 'test.pdf'
    batch_size = 2

    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Word " * 200
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    def side_effect(*args, **kwargs):
        if mock_generate_embedding.call_count == 2:
            raise Exception("Embedding generation error")
        return [0.1, 0.2, 0.3]

    mock_generate_embedding.side_effect = side_effect

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session
    mock_session.query.return_value.scalar.return_value = 1

    with patch('os.remove') as mock_os_remove:
        process_pdf_chunks(pdf_path, minio_file_name, batch_size)

    assert mock_generate_embedding.call_count >= 2
    mock_session.bulk_save_objects.assert_called()
    mock_session.commit.assert_called()
    mock_session.close.assert_called()
    mock_os_remove.assert_called_with(pdf_path)

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
def test_get_related_chunks_success(mock_create_db_and_table, mock_generate_embedding):
    question = "What is the capital of France?"
    mock_embedding = [0.1, 0.2, 0.3]
    mock_generate_embedding.return_value = mock_embedding

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session
    mock_session.query.return_value.scalar.return_value = 1

    mock_query = mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value
    mock_query.all.return_value = [MagicMock(chunk_text="Paris is the capital of France.")]


    related_chunks = get_related_chunks(question)

    mock_generate_embedding.assert_called_with(question)
    assert related_chunks == ["Paris is the capital of France."]
    mock_session.close.assert_called()

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
def test_get_related_chunks_exception(mock_create_db_and_table, mock_generate_embedding):
    question = "What is the capital of France?"
    mock_generate_embedding.side_effect = Exception("Embedding error")

    with pytest.raises(Exception) as exc_info:
        get_related_chunks(question)

    assert "Embedding error" in str(exc_info.value)

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
def test_get_related_chunks_by_filename_success(mock_create_db_and_table, mock_generate_embedding):
    query = "What is the capital of France?"
    filename = "test.pdf"
    mock_embedding = [0.1, 0.2, 0.3]
    mock_generate_embedding.return_value = mock_embedding

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session

    mock_session.query.return_value.filter.return_value.first.return_value = True


    mock_query = mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value
    mock_query.all.return_value = [MagicMock(chunk_text="Paris is the capital of France.")]


    related_chunks = get_related_chunks_by_filename(query, filename)


    mock_generate_embedding.assert_called_with(query)
    assert related_chunks == ["Paris is the capital of France."]
    mock_session.close.assert_called()

@patch('backend.services.queryService.generate_embedding')
@patch('backend.services.queryService.create_db_and_table')
def test_get_related_chunks_by_filename_not_found(mock_create_db_and_table, mock_generate_embedding):

    query = "What is the capital of France?"
    filename = "nonexistent.pdf"
    mock_embedding = [0.1, 0.2, 0.3]
    mock_generate_embedding.return_value = mock_embedding


    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session


    mock_session.query.return_value.filter.return_value.first.return_value = None


    with pytest.raises(HTTPException) as exc_info:
        get_related_chunks_by_filename(query, filename)

    assert exc_info.value.status_code == 404
    assert f"No records found for filename: {filename}" in exc_info.value.detail
    mock_session.close.assert_called()
