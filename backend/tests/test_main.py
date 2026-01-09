import os 
import sys
# Добавляем путь к backend для импорта модулей из пакета src
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app 

client = TestClient(app)

@pytest.fixture(scope="module")
def create_temp_pdf():
    """Создание временного PDF файла для тестирования."""
    pdf_path = "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n%....")  # Минимальный заголовок PDF для теста
    yield pdf_path
    if os.path.exists(pdf_path):
        os.remove(pdf_path)  # Удаление файла после теста

@pytest.fixture(scope="module")
def create_temp_text_file():
    """Создание временного текстового файла для тестирования."""
    text_path = "test.txt"
    with open(text_path, "wb") as f:
        f.write(b"Sample text content for testing")
    yield text_path
    if os.path.exists(text_path):
        os.remove(text_path)  # Удаление файла после теста

def test_root():
    """Тестирование корневого эндпоинта."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_upload_patent_valid_pdf(create_temp_pdf):
    """Тестирование загрузки корректного PDF файла."""
    # Мокируем функции извлечения текста и обработки сплавов
    mock_extracted_text = "Sample patent text"
    mock_metadata = {"pages": 5}
    mock_alloy_info = "Alloy composition: Fe 70%, Cr 20%, Ni 10%"
    
    with patch('src.main.extract_text_from_pdf', return_value=(mock_extracted_text, mock_metadata)), \
         patch('src.main.extract_alloy_info_from_text', return_value=mock_alloy_info):
        with open(create_temp_pdf, "rb") as f:
            response = client.post("/patent", files={"file": ("test.pdf", f, "application/pdf")})

        assert response.status_code == 200
        assert response.json()["status"] == "processed"
        assert "extracted_text" in response.json()
        assert response.json()["extracted_text"] == mock_extracted_text
        assert "metadata" in response.json()
        assert response.json()["metadata"] == mock_metadata
        assert "alloy_info" in response.json()
        assert response.json()["alloy_info"] == mock_alloy_info

def test_upload_patent_invalid_file(create_temp_text_file):
    """Тестирование загрузки некорректного файла (текстового)."""
    # Мокируем extract_text_from_pdf чтобы он выбрасывал ValueError для невалидного файла
    with patch('src.main.extract_text_from_pdf', side_effect=ValueError("неверный формат файла")):
        with open(create_temp_text_file, "rb") as f:
            response = client.post("/patent", files={"file": ("test.txt", f, "text/plain")})

        assert response.status_code == 400
        assert "detail" in response.json()
        assert "неверный формат файла" in response.json()["detail"]
