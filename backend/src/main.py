"""Patent API module for patent management and processing."""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils.pdf_text_extractor import extract_text_from_pdf, is_pdf_file

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
    """Возвращает приветственное сообщение для проверки работы API."""
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
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Проверка, является ли файл PDF
    if not is_pdf_file(file_location):
        return {"error": "Неверный PDF файл"}

    # Извлечение текста из PDF
    try:
        extracted_text, metadata = extract_text_from_pdf(file_location)
        return {
            "message": "Файл патента успешно получен и обработан",
            "status": "processed",
            "extracted_text": extracted_text,
            "metadata": metadata
        }
    except Exception as e:
        return {"error": f"Произошла ошибка при обработке PDF: {str(e)}"}
