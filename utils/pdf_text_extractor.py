#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Tuple
import os
import io
import logging

# ---- Настройка логирования ----
logger = logging.getLogger("pdf_text_extractor")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


# ---- Утилиты ----
def is_pdf_file(path: str) -> bool:
    """
    Быстрая проверка — существует ли файл и похоже ли он на PDF:
    1. расширение .pdf (не строгое требование, но удобно)
    2. первые байты '%PDF'
    """
    if not os.path.isfile(path):
        logger.debug("Файл не найден: %s", path)
        return False

    # Быстрый check по расширению (но не достаточный)
    _, ext = os.path.splitext(path)
    if ext.lower() != ".pdf":
        logger.debug("Неверное расширение: %s", ext)
        # не возвращаем False сразу — проверим магические байты ниже

    try:
        with open(path, "rb") as f:
            header = f.read(4)
            if header == b"%PDF":
                return True
            else:
                logger.debug("Магические байты не соответствуют PDF: %r", header)
                return False
    except Exception as e:
        logger.exception("Ошибка при чтении файла для проверки PDF: %s", e)
        return False


# ---- Основные функции ----
def extract_text_from_pdf(
    pdf_path: str,
    *,
    preserve_layout: bool = True,
    image_marker: str = "[IMAGE_HERE page:{page} count:{count}]",
    min_chars_for_page: int = 1,
) -> Tuple[str, dict]:
    """
    Извлечь текст из pdf_path и вернуть (text, metadata).

    - preserve_layout: если True, используем стандартный режим pdfplumber, который пытается
      сохранить относительные отступы/переносы. (pdfplumber не даёт perfect WYSIWYG,
      но обычно сохраняет много структуры).
    - image_marker: шаблон пометки для страниц с изображениями. Поддерживает {page} и {count}.
    - min_chars_for_page: если извлечённый текст страницы короче этого числа, считаем страницу "пустой".
    Возвращает общий текст (строки страниц соединены двумя переводами строки) и metadata:
      metadata = {
        "pages": <кол-во страниц в pdf>,
        "pages_with_images": <кол-во>,
        "per_page": [
            {"page_number": i, "chars": n, "has_images": bool, "image_count": k}
            ...
        ]
      }
    """
    # Отложенный импорт, чтобы код не падал при отсутствии библиотеки на этапе импорта модуля
    try:
        import pdfplumber
    except Exception as e:
        raise ImportError(
            "pdfplumber не установлен. Установите через: pip install pdfplumber"
        ) from e

    if not is_pdf_file(pdf_path):
        raise ValueError(f"Файл {pdf_path!r} не похож на PDF или недоступен.")

    logger.info("Открываем PDF: %s", pdf_path)
    pages_text = []
    metadata = {"pages": 0, "pages_with_images": 0, "per_page": []}

    with pdfplumber.open(pdf_path) as pdf:
        metadata["pages"] = len(pdf.pages)
        logger.info("Страниц в документе: %d", metadata["pages"])

        for i, page in enumerate(pdf.pages, start=1):
            # Попытка извлечь текст с сохранением структуры
            try:
                if preserve_layout:
                    # page.extract_text() пытается сохранить переносы/отступы
                    page_text = page.extract_text() or ""
                else:
                    # Можно здесь использовать другие подходы (extract_words и т.п.)
                    page_text = page.extract_text() or ""
            except Exception as e:
                logger.warning("Не удалось извлечь текст со страницы %d: %s", i, e)
                page_text = ""

            # Учитываем наличие изображений — pdfplumber хранит их в page.images
            image_count = 0
            try:
                imgs = getattr(page, "images", None)
                if imgs is None:
                    # некоторые версии/форматы могут требовать доступа через page.objects.get("image")
                    objs = getattr(page, "objects", None)
                    if objs:
                        image_count = len(objs.get("image", []))
                    else:
                        image_count = 0
                else:
                    image_count = len(imgs)
            except Exception:
                image_count = 0

            has_images = image_count > 0
            if has_images:
                metadata["pages_with_images"] += 1

            # Если текст пустой / слишком короткий — можно пометить это
            chars = len(page_text.strip())
            entry = {"page_number": i, "chars": chars, "has_images": has_images, "image_count": image_count}
            metadata["per_page"].append(entry)

            # Если есть изображения, добавим маркер в конец страницы
            if has_images:
                # добавляем пустую строку перед маркером для читаемости
                marker = image_marker.format(page=i, count=image_count)
                if page_text and not page_text.endswith("\n"):
                    page_text = page_text + "\n\n" + marker + "\n"
                else:
                    page_text = page_text + marker + "\n"

            # Если страница почти пустая, оставим пустую строку-плейсхолдер
            if chars < min_chars_for_page and not has_images:
                # чтобы не потерять страницу в номерах, вставляем заметку
                page_text = page_text + ("\n" if page_text else "")  # оставим пустую страницу

            pages_text.append(page_text)

    # Соединяем страницы — двойной перевод строки между страницами помогает сохранить вид
    full_text = "\n\n".join(pages_text).strip() + "\n"
    return full_text, metadata


def save_text_to_file(text: str, out_path: str, encoding: str = "utf-8") -> None:
    """
    Сохранить текст в файл out_path (перезапишет если уже существует).
    По умолчанию кодировка UTF-8.
    """
    # Пробуем создать папку, если нужно
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(out_path, "w", encoding=encoding) as f:
        f.write(text)
    logger.info("Сохранено в: %s (encoding=%s)", out_path, encoding)


def process_pdf_to_txt(
    pdf_path: str,
    out_txt_path: Optional[str] = None,
    *,
    preserve_layout: bool = True,
    image_marker: str = "[IMAGE_HERE page:{page} count:{count}]",
) -> dict:
    """
    Упрощённая обвязка:
      process_pdf_to_txt("a.pdf", "a.txt")
    Вернёт metadata (см. extract_text_from_pdf).
    """
    if out_txt_path is None:
        base, _ = os.path.splitext(pdf_path)
        out_txt_path = base + ".txt"

    text, metadata = extract_text_from_pdf(
        pdf_path,
        preserve_layout=preserve_layout,
        image_marker=image_marker,
    )
    save_text_to_file(text, out_txt_path)
    metadata["output_txt"] = out_txt_path
    return metadata


# ---- CLI (пример использования) ----
def _cli():
    """
    Простой command-line интерфейс:
      python pdf_text_extractor.py input.pdf -o output.txt
    """
    import argparse
    parser = argparse.ArgumentParser(description="Извлечение текста из PDF с использованием pdfplumber.")
    parser.add_argument("pdf", help="Путь к входному PDF")
    parser.add_argument("-o", "--out", help="Путь к выходному .txt (по умолчанию берётся тот же базовый путь)", default=None)
    parser.add_argument("--no-layout", help="Не пытаться сохранять верстку (меньше пробелов/переносов).", action="store_true")
    parser.add_argument("--image-marker", help="Шаблон маркера для изображений (поддерживает {page} и {count})",
                        default="[IMAGE_HERE page:{page} count:{count}]")
    args = parser.parse_args()

    try:
        meta = process_pdf_to_txt(
            args.pdf,
            args.out,
            preserve_layout=not args.no_layout,
            image_marker=args.image_marker,
        )
        logger.info("Готово. Метаданные: %s", meta)
    except Exception as e:
        logger.exception("Не удалось обработать PDF: %s", e)


if __name__ == "__main__":
    _cli()
