import io

import pdfplumber
from fastapi import UploadFile


def extract_text_from_pdf_file(file: UploadFile) -> str:
    """
    Извлекает текст из PDF-файла, переданного как UploadFile (FastAPI).

    - Не сохраняет файл на диск
    - Не сохраняет верстку
    - Возвращает весь текст одной строкой
    - Подходит для дальнейшего NLP / парсинга

    :param file: UploadFile (FastAPI), PDF файл
    :return: Текст из PDF в виде строки
    """

    # Быстрая проверка типа (дополнительная защита)
    if file.content_type != "application/pdf":
        raise ValueError("Переданный файл не является PDF")

    # Читаем файл целиком в память
    pdf_bytes = file.file.read()

    # Простая проверка сигнатуры PDF
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("Файл не похож на PDF (нет сигнатуры %PDF)")

    extracted_pages: list[str] = []

    # Открываем PDF из памяти
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            # pdfplumber сам решает, как извлечь текст
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)

    # Склеиваем страницы в одну строку
    full_text = "\n\n".join(extracted_pages).strip()

    return full_text
