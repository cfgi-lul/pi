"""Patent API module for patent management and processing."""
import os

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pdf_text_extractor import (  # pylint: disable=import-error
    extract_text_from_pdf,
    extract_alloy_info_from_text
)

app = FastAPI(
    title="Patent API",
    description="API for patent management and processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS to allow requests from Angular frontend
# Настраивает CORS для разрешения запросов от Angular фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Hello World"}


@app.post("/patent")
async def upload_patent(file: UploadFile = File(...)):
    """
    Загрузка PDF файла для обработки патента.

    Аргументы:
        file: PDF файл для загрузки

    Возвращает:
        Результат обработки PDF
    """
    # Сохранение загруженного файла временно
    file_location = f"/tmp/{file.filename}"
    try:
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
    except (IOError, OSError) as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}"
        ) from e

    # Извлечение текста из PDF
    try:
        print(f"[PDF] Начало обработки файла: {file.filename}", flush=True)
        extracted_text, metadata = extract_text_from_pdf(file_location)
        pages = metadata.get('pages', 'N/A')
        chars = len(extracted_text)
        print(f"[PDF] Текст извлечен. Страниц: {pages}, "
              f"Символов: {chars}", flush=True)

        # Извлечение информации об сплавах из текста патента
        print("[PDF] Начало извлечения информации об сплавах...", flush=True)
        alloy_info = extract_alloy_info_from_text(extracted_text)
        print("[PDF] Извлечение информации об сплавах завершено", flush=True)
        # Удаляем временный файл после обработки
        if os.path.exists(file_location):
            os.remove(file_location)
        return {
            "message": "Файл патента успешно получен и обработан",
            "status": "processed",
            "extracted_text": extracted_text,
            "metadata": metadata,
            "alloy_info": alloy_info
        }
    except ValueError as e:
        # Удаляем временный файл при ошибке
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (FileNotFoundError, OSError) as e:
        # Удаляем временный файл при ошибке
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=500,
            detail=f"Произошла ошибка при обработке PDF: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
