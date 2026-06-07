"""Step 2 - OCR a captured frame to stdout.

Dumb-but-runnable only: read one PNG, run default Tesseract OCR, return text.
No ROI cropping, layout analysis, task detection, context building, model calls,
overlay, or logger.
"""
from pathlib import Path

import pytesseract
from PIL import Image


def ocr_image_to_text(path: Path) -> str:
    """Run default OCR over a captured PNG and return raw text."""
    with Image.open(path) as image:
        return pytesseract.image_to_string(image)


def print_ocr_result(path: Path) -> None:
    """Print OCR output in a visible, bounded stdout block."""
    try:
        text = ocr_image_to_text(path).strip()
    except pytesseract.TesseractNotFoundError:
        print("[ocr] FAILED: tesseract binary not found")
        print("[ocr] install hint: brew install tesseract")
        return
    except Exception as exc:
        print(f"[ocr] FAILED: {exc!r}")
        return

    print_ocr_text(text)


def print_ocr_text(text: str) -> None:
    """Print already-computed OCR text without running OCR again."""
    cleaned = text.strip()
    print("[ocr] begin")
    if cleaned:
        print(cleaned)
    else:
        print("[ocr] no text detected")
    print("[ocr] end")
