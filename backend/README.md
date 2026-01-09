# Patent API

API для обработки и управления патентными документами в формате PDF.

## Описание

Patent API — это FastAPI-приложение для загрузки, проверки и извлечения текста из патентных PDF-файлов. Сервис предоставляет RESTful API для интеграции с фронтенд-приложениями (например, Angular).

## Основные возможности

- Загрузка PDF-файлов патентов через API
- Автоматическая проверка формата файлов (сигнатура PDF)
- Извлечение текста из PDF без сохранения на диск
- CORS настройка для безопасной работы с фронтендом
- Метаданные обработки файлов
- Обработка ошибок с детальными сообщениями

## Быстрый старт

### Предварительные требования

- Python 3.8+
- pip (менеджер пакетов Python)

### Установка

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd patent-api
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

Или установите FastAPI со стандартными зависимостями напрямую:

```bash
pip install "fastapi[standard]"
pip install pdfplumber pylint pycodestyle
```

3. Запустите приложение:

**Рекомендуемый способ: через FastAPI CLI**

Из директории `src/`:

```bash
cd src
fastapi dev main.py
```

Или из корневой директории `backend/`:

```bash
fastapi dev src/main.py
```

**Альтернативные способы:**

Через uvicorn напрямую:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Или через Python:

```bash
cd src
python main.py
```

После запуска приложение будет доступно по адресу:
- API: http://localhost:8000
- Документация Swagger: http://localhost:8000/docs
- Документация ReDoc: http://localhost:8000/redoc

## Структура проекта

```
backend/
├── src/
│   ├── main.py              # Основной файл FastAPI приложения
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pdf_text_extractor.py  # Модуль для извлечения текста из PDF
├── requirements.txt     # Зависимости Python
├── README.md           # Эта документация
└── tests/              # Тесты (рекомендуется добавить)
```

## Зависимости

Основные зависимости указаны в `requirements.txt`:

- `fastapi[standard]>=0.122.0` - Веб-фреймворк со стандартными зависимостями (включая uvicorn)
- `pdfplumber>=0.11.0` - Извлечение текста из PDF
- `pylint>=3.0.0` - Линтинг кода
- `pycodestyle>=2.11.0` - Проверка стиля кода

## API Endpoints

### 1. GET /

Проверка работоспособности API.

**Ответ:**

```json
{
  "message": "Hello World"
}
```

### 2. POST /patent

Загрузка и обработка PDF-файла патента.

**Параметры:**

- `file`: PDF файл (multipart/form-data)

**Успешный ответ:**

```json
{
  "message": "Файл патента успешно получен и обработан",
  "status": "processed",
  "extracted_text": "Извлеченный текст из PDF...",
  "metadata": {}
}
```

**Ошибки:**

- `400`: Неверный формат файла
- `500`: Ошибка при обработке PDF

## Использование

### Пример запроса с cURL

```bash
curl -X POST "http://localhost:8000/patent" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/patent.pdf"
```

### Пример запроса с Python (requests)

```python
import requests

url = "http://localhost:8000/patent"
files = {"file": open("patent.pdf", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

### Интеграция с Angular

```typescript
import { HttpClient } from '@angular/common/http';

uploadPatent(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  return this.http.post('http://localhost:8000/patent', formData);
}
```

## Тестирование

Проект использует `pytest` для тестирования. Убедитесь, что `pytest` установлен:

```bash
pip install -r requirements.txt
```

### Способы запуска тестов:

**1. Запустить все тесты:**
```bash
cd backend
python3 -m pytest tests/
```

или просто:
```bash
python3 -m pytest tests/
```

**2. Запустить тесты с подробным выводом:**
```bash
python3 -m pytest tests/ -v
```

**3. Запустить конкретный файл с тестами:**
```bash
python3 -m pytest tests/test_main.py
python3 -m pytest tests/test_pdf_extractor.py
```

**4. Запустить конкретный тест:**
```bash
python3 -m pytest tests/test_main.py::test_root
```

**5. Запустить тесты с выводом print-ов:**
```bash
python3 -m pytest tests/ -v -s
```

**6. Запустить тесты и показать покрытие (требуется pytest-cov):**
```bash
pip install pytest-cov
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Структура тестов:

```
tests/
├── test_main.py              # Тесты для FastAPI endpoints
└── test_pdf_extractor.py     # Тесты для извлечения текста из PDF
```

## Стиль кода

```bash
# Проверка стиля
pycodestyle --max-line-length=100 main.py utils/

# Линтинг
pylint main.py utils/
```
