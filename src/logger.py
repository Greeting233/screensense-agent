"""Step 7 - request-level JSONL logger.

Minimal request-level logging only. No event stream, async writer, rotation,
database, retry, routing, cache, or evaluation logic.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


DEFAULT_LOG_PATH = Path("data/logs/runtime_log.jsonl")
VALID_STATUSES = {"success", "cancelled", "failed"}


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def context_components(context: dict[str, str] | None) -> list[str]:
    """Return context keys as the v0 component list."""
    if not context:
        return []
    return list(context.keys())


def context_size(context: dict[str, str] | None) -> dict[str, int | None]:
    """Measure v0 context scale without counting JSON syntax."""
    if not context:
        return {"chars": 0, "blocks": None}
    chars = sum(len(str(value)) for value in context.values() if value is not None)
    return {"chars": chars, "blocks": None}


def build_log_record(
    *,
    request_id: int,
    ts_start: str,
    ts_end: str,
    status: str,
    task: str | None,
    context: dict[str, str] | None,
    model: str | None,
    prompt_tokens: int | None,
    t_capture: int,
    t_ocr: int,
    t_vision: int,
    t_context: int,
    t_llm: int,
    t_render: int,
    t_total: int,
    suggestion_present: bool,
    overlay_shown: bool,
    cancelled_by_newer_request: bool,
    error_type: str | None,
    cpu_pct: float | None = None,
    mem_mb: float | None = None,
) -> dict[str, Any]:
    """Build one request-level log record."""
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid log status: {status}")

    return {
        "request_id": request_id,
        "ts_start": ts_start,
        "ts_end": ts_end,
        "status": status,
        "task": task,
        "context_components": context_components(context),
        "context_size": context_size(context),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "t_capture": t_capture,
        "t_ocr": t_ocr,
        "t_vision": t_vision,
        "t_context": t_context,
        "t_llm": t_llm,
        "t_render": t_render,
        "t_total": t_total,
        "suggestion_present": suggestion_present,
        "overlay_shown": overlay_shown,
        "cancelled_by_newer_request": cancelled_by_newer_request,
        "error_type": error_type,
        "cpu_pct": cpu_pct,
        "mem_mb": mem_mb,
    }


def append_log_record(record: dict[str, Any], path: Path | str = DEFAULT_LOG_PATH) -> None:
    """Append one JSON record to a JSONL file."""
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
