import os 
import sys
sys.path.insert(0, "C:/Users/Win10/pi/backend/src")
import pytest
from unittest.mock import patch, MagicMock
from src.pdf_text_extractor import extract_text_from_pdf

def test_extract_text_from_pdf():
    # Создаем поддельный объект PDF
    mock_pdf = MagicMock()
    mock_page = MagicMock()

    # Задаем поведение для поддельной страницы
    mock_page.extract_text.return_value = "Sample text from page 1"
    mock_pdf.pages = [mock_page]  # Список страниц

    # Настраиваем mock для pdfplumber.open
    with patch('pdfplumber.open', return_value=mock_pdf):
        file_path = 'test.pdf'  # Путь к тестовому PDF (можно указать любой строковый путь)

        # Вызываем функцию
        extracted_text, metadata = extract_text_from_pdf(file_path)

        # Отладочный вывод
        print(f"Extracted Text: '{extracted_text}'")  # Выводим извлеченный текст
        print(f"Metadata: {metadata}")  # Выводим метаданные

        # Проверяем результаты
        assert extracted_text == "Sample text from page 1"
        assert metadata['pages'] == 1

if __name__ == '__main__':
    pytest.main()
