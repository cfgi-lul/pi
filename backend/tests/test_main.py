import os 
import sys
sys.path.insert(0, "C:/Users/Win10/pi/backend/src")
import pytest
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

@pytest.fixture(scope="module")
def create_temp_pdf():
    """Создание временного PDF файла для тестирования."""
    pdf_path = "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n%....")  # Минимальный заголовок PDF для теста
    yield pdf_path
    os.remove(pdf_path)  # Удаление файла после теста

def test_root():
    """Тестирование корневого эндпоинта."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_upload_patent_valid_pdf(create_temp_pdf):
    """Тестирование загрузки корректного PDF файла."""
    with open(create_temp_pdf, "rb") as f:
        response = client.post("/patent", files={"file": ("test.pdf", f, "application/pdf")})

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert "extracted_text" in response.json()
    assert "metadata" in response.json()

def test_upload_patent_invalid_file(create_temp_text_file):
    """Тестирование загрузки некорректного файла (текстового)."""
    with open(create_temp_text_file, "rb") as f:
        response = client.post("/patent", files={"file": ("test.txt", f, "text/plain")})

    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Ошибка при обработке PDF: неверный формат файла"
