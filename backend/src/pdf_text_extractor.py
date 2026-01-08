"""Module for extracting text from PDF files."""
import pdfplumber


def extract_text_from_pdf(file_path: str) -> tuple[str, dict]:
    """
    Извлекает текст из PDF-файла по пути.

    :param file_path: Путь к PDF файлу
    :return: Кортеж (извлеченный текст, метаданные)
    """
    extracted_pages: list[str] = []
    metadata = {}

    with pdfplumber.open(file_path) as pdf:
        metadata["pages"] = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)

    full_text = "\n\n".join(extracted_pages).strip()
    return full_text, metadata
