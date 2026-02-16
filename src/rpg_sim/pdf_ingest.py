from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class SourceChunk:
    id: str
    page_start: int
    page_end: int
    word_count: int
    text: str


def ingest_pdf_to_chunks(
    pdf_path: str | Path,
    output_path: str | Path,
    chunk_words: int = 220,
    chunk_overlap_words: int = 40,
) -> dict:
    source = Path(pdf_path)
    if not source.exists():
        raise FileNotFoundError(f"PDF not found: {source}")
    if chunk_words <= 0:
        raise ValueError("chunk_words must be positive")
    if chunk_overlap_words < 0:
        raise ValueError("chunk_overlap_words cannot be negative")
    if chunk_overlap_words >= chunk_words:
        raise ValueError("chunk_overlap_words must be smaller than chunk_words")

    reader = PdfReader(str(source))

    page_texts = _extract_page_texts(reader)
    if not page_texts:
        page_texts = _extract_page_texts_ocr(source, total_pages=len(reader.pages))

    chunks = _chunk_pages(
        page_texts=page_texts,
        chunk_words=chunk_words,
        chunk_overlap_words=chunk_overlap_words,
    )

    payload = {
        "source_file": str(source),
        "total_pages": len(reader.pages),
        "pages_with_text": len(page_texts),
        "chunk_words": chunk_words,
        "chunk_overlap_words": chunk_overlap_words,
        "chunk_count": len(chunks),
        "chunks": [asdict(chunk) for chunk in chunks],
    }

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return payload


def load_chunk_texts(path: str | Path, max_chunks: int = 800) -> list[str]:
    source = Path(path)
    if not source.exists():
        return []

    with source.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    chunks = payload.get("chunks", [])
    if not isinstance(chunks, list):
        return []

    texts = [chunk.get("text", "") for chunk in chunks if isinstance(chunk, dict)]
    texts = [text for text in texts if isinstance(text, str) and text.strip()]
    return texts[:max_chunks]


def _extract_page_texts(reader: PdfReader) -> list[tuple[int, str]]:
    page_texts: list[tuple[int, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized = _normalize_text(text)
        if normalized:
            page_texts.append((index, normalized))
    return page_texts


def _extract_page_texts_ocr(pdf_path: Path, total_pages: int) -> list[tuple[int, str]]:
    if shutil.which("tesseract") is None:
        return []

    try:
        import pypdfium2 as pdfium
        import pytesseract
    except Exception:
        return []

    page_texts: list[tuple[int, str]] = []
    try:
        document = pdfium.PdfDocument(str(pdf_path))
    except Exception:
        return []

    for index in range(0, min(len(document), total_pages)):
        try:
            page = document[index]
            bitmap = page.render(scale=2)
            image = bitmap.to_pil()
            text = pytesseract.image_to_string(image)
            normalized = _normalize_text(text)
            if normalized:
                page_texts.append((index + 1, normalized))
        except Exception:
            continue

    return page_texts


def _chunk_pages(
    page_texts: list[tuple[int, str]],
    chunk_words: int,
    chunk_overlap_words: int,
) -> list[SourceChunk]:
    chunks: list[SourceChunk] = []

    words_with_page: list[tuple[str, int]] = []
    for page_number, text in page_texts:
        words = text.split()
        words_with_page.extend((word, page_number) for word in words)

    if not words_with_page:
        return chunks

    step = chunk_words - chunk_overlap_words
    chunk_id = 1
    start = 0
    total = len(words_with_page)

    while start < total:
        end = min(start + chunk_words, total)
        window = words_with_page[start:end]
        words = [entry[0] for entry in window]
        pages = [entry[1] for entry in window]
        text = " ".join(words).strip()

        if text:
            chunks.append(
                SourceChunk(
                    id=f"chunk-{chunk_id:05d}",
                    page_start=min(pages),
                    page_end=max(pages),
                    word_count=len(words),
                    text=text,
                )
            )
            chunk_id += 1

        start += step

    return chunks


def _normalize_text(text: str) -> str:
    cleaned = text.replace("\x00", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()