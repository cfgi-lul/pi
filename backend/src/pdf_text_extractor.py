"""Module for extracting text from PDF files."""
import multiprocessing
import os
import time
from contextlib import redirect_stderr
from io import StringIO
from typing import Dict, List, Optional, Tuple

import pdfplumber
from llama_cpp import Llama


def split_text_into_chunks(
    text: str,
    chunk_size: int = 2000,
    overlap: int = 0
) -> List[str]:
    """
    Разбивает текст на чанки заданного размера.

    :param text: Текст для разбиения
    :param chunk_size: Размер чанка в символах
    :param overlap: Перекрытие между чанками в символах
    :return: Список текстовых чанков
    """
    if not text or not text.strip():
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)

        if end >= len(text):
            break
        start = end - overlap

    return chunks


def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict]:
    """
    Извлекает текст из PDF-файла по пути.

    :param file_path: Путь к PDF файлу
    :return: Кортеж (извлеченный текст, метаданные)
    """
    print(f"[PDF] Открытие PDF файла: {file_path}", flush=True)
    extracted_pages: List[str] = []
    metadata = {}

    with pdfplumber.open(file_path) as pdf:
        metadata["pages"] = len(pdf.pages)
        pages_count = metadata['pages']
        print(f"[PDF] Всего страниц в документе: {pages_count}",
              flush=True)
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)
                if i % 10 == 0 or i == metadata["pages"]:
                    print(f"[PDF] Обработано страниц: {i}/{pages_count}",
                          flush=True)

    full_text = "\n\n".join(extracted_pages).strip()
    chars_count = len(full_text)
    print(f"[PDF] Извлечение текста завершено. "
          f"Всего символов: {chars_count}", flush=True)
    return full_text, metadata


def _process_single_chunk(
    chunk_text: str,
    llm: Llama,
    chunk_num: int = 0,
    total_chunks: int = 0
) -> str:
    """Обрабатывает один чанк текста через LLM."""
    chunk_size = len(chunk_text)
    if total_chunks > 0:
        msg = f"[LLM] Обработка чанка {chunk_num + 1}/{total_chunks} "
        msg += f"(размер: {chunk_size} символов)..."
        print(msg, flush=True)
    else:
        print(f"[LLM] Обработка чанка (размер: {chunk_size} символов)...",
              flush=True)

    start_time = time.time()

    prompt_template = (
        "Extract all explicitly stated information about metallic alloys "
        "from the text.\n"
        "List each property on a new line in format: "
        "\"Property name: value\"\n"
        "Use original wording and units from the text.\n"
        "If no alloy information found, write \"No alloy information\".\n\n"
        "Example:\n"
        "Melting temperature: 1600 °C\n"
        "Alloy composition: Fe 70%, Cr 20%, Ni 10%\n"
        "Hardness: 350 HB\n\n"
        "Text:\n"
    )
    prompt = prompt_template + chunk_text

    max_prompt_chars = 3500
    if len(prompt) > max_prompt_chars:
        max_text_chars = max_prompt_chars - len(prompt_template)
        chunk_text = chunk_text[:max_text_chars]
        prompt = prompt_template + chunk_text

    response = llm(
        prompt,
        temperature=0.0,
        top_p=0.9,
        top_k=20,
        max_tokens=500,
        repeat_penalty=1.1,
        stop=["\n\nText:", "\n\nText"],
        echo=False
    )

    output_text = response["choices"][0]["text"].strip()

    elapsed_time = time.time() - start_time
    if total_chunks > 0:
        msg = f"[LLM] Чанк {chunk_num + 1}/{total_chunks} "
        msg += f"обработан за {elapsed_time:.1f}с"
        print(msg, flush=True)
    else:
        print(f"[LLM] Чанк обработан за {elapsed_time:.1f}с", flush=True)

    if output_text:
        chunk_info = f"{chunk_num + 1}" if total_chunks > 0 else ""
        print(f"[LLM] Ответ по чанку {chunk_info}:", flush=True)
        print(output_text, flush=True)
        print("-" * 80, flush=True)
    else:
        chunk_info = f"{chunk_num + 1}" if total_chunks > 0 else ""
        print(f"[LLM] Пустой ответ по чанку {chunk_info}", flush=True)

    return output_text


def _load_llm_model(model_path: str, cpu_count: int) -> Llama:
    """
    Загружает LLM модель с попытками использования GPU.

    :param model_path: Путь к модели
    :param cpu_count: Количество CPU потоков
    :return: Загруженная модель Llama
    """
    with redirect_stderr(StringIO()):
        try:
            llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=cpu_count,
                n_batch=1024,
                n_gpu_layers=32,
                use_mmap=True,
                use_mlock=False,
                verbose=False
            )
            print("[LLM] Модель Mistral загружена с GPU ускорением (32 слоя)",
                  flush=True)
            return llm
        except (RuntimeError, OSError) as e:
            error_msg = str(e)
            msg = "[LLM] Предупреждение: не удалось загрузить с полным GPU "
            msg += f"({error_msg}), пробуем с меньшим количеством слоев..."
            print(msg, flush=True)
            try:
                llm = Llama(
                    model_path=model_path,
                    n_ctx=4096,
                    n_threads=cpu_count,
                    n_batch=1024,
                    n_gpu_layers=16,
                    use_mmap=True,
                    verbose=False
                )
                print("[LLM] Модель Mistral загружена с частичным "
                      "GPU ускорением (16 слоев)", flush=True)
                return llm
            except (RuntimeError, OSError):
                print("[LLM] Используем только CPU", flush=True)
                llm = Llama(
                    model_path=model_path,
                    n_ctx=4096,
                    n_threads=cpu_count,
                    n_batch=1024,
                    n_gpu_layers=0,
                    use_mmap=True,
                    verbose=False
                )
                return llm


def _process_chunks(chunks: List[str], llm: Llama) -> List[str]:
    """
    Обрабатывает все чанки текста через LLM.

    :param chunks: Список текстовых чанков
    :param llm: Загруженная модель LLM
    :return: Список сводок по каждому чанку
    """
    summaries: List[str] = []

    for i, chunk in enumerate(chunks):
        if not chunk or not chunk.strip():
            continue
        chunk_summary = _process_single_chunk(
            chunk, llm, chunk_num=i, total_chunks=len(chunks)
        )
        if chunk_summary.strip():
            summaries.append(chunk_summary)

    return summaries


def _build_final_summary(
    summaries: List[str],
    llm: Llama
) -> str:
    """Собирает финальный ответ из всех сводок."""
    print("[LLM] Сборка финального ответа из всех записей...", flush=True)
    start_time = time.time()

    valid_summaries = [
        s.strip() for s in summaries
        if s.strip() and "No alloy information" not in s.lower()
    ]
    if not valid_summaries:
        print("[LLM] Нет данных для сборки", flush=True)
        return ""

    combined_summaries = "\n\n".join(
        [f"Запись {i+1}:\n{s}" for i, s in enumerate(valid_summaries)]
    )

    prompt_template = (
        "Combine all information about metallic alloys from the "
        "summaries below.\n"
        "List each property on a new line in format: "
        "\"Property name: value\"\n"
        "Merge duplicates - if the same property appears multiple "
        "times, keep the most complete version.\n"
        "Use original wording and units.\n\n"
        "Example:\n"
        "Melting temperature: 1600 °C\n"
        "Alloy composition: Fe 70%, Cr 20%, Ni 10%\n"
        "Hardness: 350 HB\n\n"
        "Summaries:\n"
    )
    prompt = prompt_template + combined_summaries

    max_prompt_chars = 3500
    if len(prompt) > max_prompt_chars:
        max_summaries_chars = max_prompt_chars - len(prompt_template)
        combined_summaries = combined_summaries[:max_summaries_chars]
        prompt = prompt_template + combined_summaries

    response = llm(
        prompt,
        temperature=0.0,
        top_p=0.9,
        top_k=20,
        max_tokens=1000,
        repeat_penalty=1.1,
        stop=["\n\nSummaries", "\n\nSummaries:"],
        echo=False
    )

    output_text = response["choices"][0]["text"].strip()

    elapsed_time = time.time() - start_time
    print(f"[LLM] Финальный ответ собран за {elapsed_time:.1f}с", flush=True)
    return output_text


def extract_alloy_info_from_text(
    patent_text: str,
    model_path: Optional[str] = None,
    chunk_size: int = 2000,
    overlap: int = 0
) -> str:
    """
    Извлекает информацию о сплавах из текста патента с помощью LLM.

    :param patent_text: Текст патента для обработки
    :param model_path: Путь к модели LLM (опционально)
    :param chunk_size: Размер чанка для обработки
    :param overlap: Перекрытие между чанками
    :return: Извлеченная информация о сплавах
    """
    if model_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(
            current_dir, "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        )

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Модель не найдена по пути: {model_path}"
        )

    if not patent_text or not patent_text.strip():
        print("[LLM] Ошибка: текст патента пустой", flush=True)
        return ""

    text_size = len(patent_text)
    print(f"[LLM] Начало обработки текста патента "
          f"(размер: {text_size} символов)", flush=True)
    start_total_time = time.time()

    print("[LLM] Загрузка модели...", flush=True)
    model_load_start = time.time()
    cpu_count = multiprocessing.cpu_count()
    llm = _load_llm_model(model_path, cpu_count)
    model_load_time = time.time() - model_load_start
    print(f"[LLM] Модель загружена за {model_load_time:.1f}с", flush=True)

    print(f"[LLM] Разбиение текста на чанки "
          f"(размер чанка: {chunk_size} символов)...", flush=True)
    chunks = split_text_into_chunks(patent_text, chunk_size, overlap)

    if not chunks:
        print("[LLM] Ошибка: не удалось разбить текст на чанки", flush=True)
        return ""

    print(f"[LLM] Текст разбит на {len(chunks)} чанков", flush=True)

    summaries = _process_chunks(chunks, llm)

    if summaries:
        result = _build_final_summary(summaries, llm)
    else:
        print("[LLM] Не найдено информации об сплавах", flush=True)
        result = ""

    total_time = time.time() - start_total_time
    print(f"[LLM] Обработка завершена за {total_time:.1f}с", flush=True)

    return result
