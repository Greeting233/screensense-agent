"""Step 3 - build a minimum context dict.

Dumb-but-runnable only: use OCR text, the rule-based task label, and a timestamp.
No prompt construction, no memory, no adaptive context selection, no logger.
"""
from __future__ import annotations

from datetime import datetime, timezone


def _excerpt(text: str, max_chars: int) -> str:
    """Collapse whitespace and keep a bounded excerpt."""
    collapsed = " ".join(text.split())
    return collapsed[:max_chars]


def build_context(task: str, ocr_text: str) -> dict[str, str]:
    """Build the smallest context object needed by the Step 3 stdout check."""
    return {
        "task": task,
        "terminal_text": _excerpt(ocr_text, 1200) if task != "unknown" else "",
        "editor_text_excerpt": _excerpt(ocr_text, 600) if task == "code_error" else "",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def print_context(context: dict[str, str]) -> None:
    """Print the context dict in a visible stdout block."""
    print("[context] begin")
    print(context)
    print("[context] end")
