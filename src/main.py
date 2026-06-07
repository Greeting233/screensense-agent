"""ScreenSense-Agent v0 entry point - Step 6 cancel rule.

Hotkey -> capture -> OCR -> task parsing -> context -> suggestion -> overlay.

Step 6 adds a minimal cancel rule: when a newer request starts, older in-flight
requests become stale and must not update the visible overlay. This stays inside
the suggestion-first boundary: no logger, no retry, no routing, no queue system,
and no automatic desktop action.
"""
from __future__ import annotations

import os
from pathlib import Path
import threading
import time

from platforms.macos.hotkey_macos import run_hotkey_loop
from src.capture import capture_to_path
from src.context import build_context, print_context
from src.logger import append_log_record, build_log_record, utc_now_iso
from src.ocr import ocr_image_to_text, print_ocr_text
from src.overlay import show_overlay
from src.suggestion import SuggestionResult, current_model_name, generate_suggestion_with_metadata
from src.vision import classify_task


# v0 hotkey: Ctrl + Option(Alt) + S.
# Can be overridden for diagnostics, e.g. SCREENSENSE_HOTKEY="<cmd>+<shift>+9".
HOTKEY = os.environ.get("SCREENSENSE_HOTKEY", "<ctrl>+<alt>+s")

REPO_ROOT = Path(__file__).resolve().parent.parent

_request_lock = threading.Lock()
CURRENT_REQUEST_ID = 0

_overlay_condition = threading.Condition()
_pending_overlay: tuple[int, str, str] | None = None

_log_lock = threading.Lock()
_request_log_state: dict[int, dict[str, object]] = {}


def _claim_new_request_id() -> int:
    """Claim the newest request id and make all older requests stale."""
    global CURRENT_REQUEST_ID
    with _request_lock:
        CURRENT_REQUEST_ID += 1
        return CURRENT_REQUEST_ID


def is_current_request(rid: int) -> bool:
    """Return True only when rid is still the newest request."""
    with _request_lock:
        return rid == CURRENT_REQUEST_ID


def _start_log_state(rid: int) -> None:
    """Initialize per-request log state."""
    with _log_lock:
        _request_log_state[rid] = {
            "ts_start": utc_now_iso(),
            "perf_start": time.perf_counter(),
            "task": None,
            "context": None,
            "model": current_model_name(),
            "prompt_tokens": None,
            "t_capture": 0,
            "t_ocr": 0,
            "t_vision": 0,
            "t_context": 0,
            "t_llm": 0,
            "t_render": 0,
            "suggestion_present": False,
            "overlay_shown": False,
            "finalized": False,
        }


def _update_log_state(rid: int, **fields: object) -> None:
    """Update per-request log state without appending a record."""
    with _log_lock:
        state = _request_log_state.setdefault(rid, {"ts_start": utc_now_iso()})
        state.update(fields)


def _finalize_request_log(
    rid: int,
    *,
    status: str,
    cancelled_by_newer_request: bool,
    error_type: str | None = None,
    overlay_shown: bool | None = None,
) -> None:
    """Append exactly one request-level log record."""
    with _log_lock:
        state = _request_log_state.setdefault(rid, {"ts_start": utc_now_iso()})
        if state.get("finalized"):
            return
        state["finalized"] = True
        if overlay_shown is not None:
            state["overlay_shown"] = overlay_shown
        perf_start = state.get("perf_start")
        t_total = _elapsed_ms(perf_start) if isinstance(perf_start, float) else 0

        record = build_log_record(
            request_id=rid,
            ts_start=str(state.get("ts_start")),
            ts_end=utc_now_iso(),
            status=status,
            task=state.get("task") if isinstance(state.get("task"), str) else None,
            context=state.get("context") if isinstance(state.get("context"), dict) else None,
            model=state.get("model") if isinstance(state.get("model"), str) else None,
            prompt_tokens=state.get("prompt_tokens") if isinstance(state.get("prompt_tokens"), int) else None,
            t_capture=int(state.get("t_capture", 0) or 0),
            t_ocr=int(state.get("t_ocr", 0) or 0),
            t_vision=int(state.get("t_vision", 0) or 0),
            t_context=int(state.get("t_context", 0) or 0),
            t_llm=int(state.get("t_llm", 0) or 0),
            t_render=int(state.get("t_render", 0) or 0),
            t_total=t_total,
            suggestion_present=bool(state.get("suggestion_present")),
            overlay_shown=bool(state.get("overlay_shown")),
            cancelled_by_newer_request=cancelled_by_newer_request,
            error_type=error_type,
            cpu_pct=None,
            mem_mb=None,
        )

    append_log_record(record, REPO_ROOT / "data/logs/runtime_log.jsonl")
    print(f"[logger] appended request_id={rid} status={status}")


def _cancel_request(rid: int, stage: str) -> None:
    """Mark a stale request as cancelled and append its request-level log."""
    print(f"[cancel] rid={rid} stale {stage}; abort")
    _finalize_request_log(
        rid,
        status="cancelled",
        cancelled_by_newer_request=True,
        error_type=None,
        overlay_shown=False,
    )


def _frame_path_for_request(rid: int) -> Path:
    """Use one frame file per request so concurrent A/B runs do not collide."""
    return REPO_ROOT / f"last_frame_rid_{rid}.png"


def _elapsed_ms(start: float) -> int:
    """Return elapsed monotonic time in milliseconds."""
    return max(0, int(round((time.perf_counter() - start) * 1000)))


def _suggestion_parts(result: object) -> tuple[str, str, int | None]:
    """Accept real SuggestionResult or legacy test monkeypatch strings."""
    if isinstance(result, SuggestionResult):
        return result.text, result.model, result.prompt_tokens
    return str(result), current_model_name(), None


def _debug_delay_before_suggestion(rid: int) -> None:
    """Optional validation delay for hotkey A/B testing.

    This is disabled by default. It exists only to make the formal hotkey
    validation easier when the model returns too quickly to press the second
    hotkey before request A finishes.
    """
    raw_delay = os.environ.get("SCREENSENSE_DEBUG_DELAY_SEC", "0")
    try:
        delay = float(raw_delay)
    except ValueError:
        delay = 0.0
    if delay <= 0:
        return

    print(f"[debug] rid={rid} sleeping {delay:.2f}s before suggestion")
    time.sleep(delay)


def _queue_overlay(rid: int, task: str, suggestion: str) -> None:
    """Hand the latest visible result to the main thread.

    This is a single-slot handoff, not a work queue: a newer request may replace
    an older pending overlay before it is shown, and the main thread checks the
    request id again before opening the Cocoa window.
    """
    global _pending_overlay
    with _overlay_condition:
        _pending_overlay = (rid, task, suggestion)
        _overlay_condition.notify()


def process_next_overlay(timeout: float | None = None) -> bool:
    """Show one pending overlay on the current thread.

    Returns True if an overlay was shown, False if the wait timed out or the
    pending overlay had already become stale.
    """
    global _pending_overlay
    with _overlay_condition:
        if _pending_overlay is None:
            _overlay_condition.wait(timeout=timeout)
        pending = _pending_overlay
        _pending_overlay = None

    if pending is None:
        return False

    rid, task, suggestion = pending
    if not is_current_request(rid):
        _cancel_request(rid, "before overlay")
        return False

    print(f"[overlay] showing rid={rid}")
    render_start = time.perf_counter()
    show_overlay(task=task, suggestion=suggestion)
    _update_log_state(rid, t_render=_elapsed_ms(render_start))
    _finalize_request_log(
        rid,
        status="success",
        cancelled_by_newer_request=False,
        error_type=None,
        overlay_shown=True,
    )
    return True


def run_overlay_dispatch_loop() -> None:
    """Main-thread overlay loop used by the hotkey entry point."""
    while True:
        process_next_overlay(timeout=None)


def _run_pipeline(rid: int) -> None:
    """Run one full request and stop before UI if the request becomes stale."""
    output_path = _frame_path_for_request(rid)

    try:
        stage_start = time.perf_counter()
        capture_to_path(output_path)
        _update_log_state(rid, t_capture=_elapsed_ms(stage_start))
        print(f"[capture] saved {output_path} (rid={rid})")
        if not is_current_request(rid):
            _cancel_request(rid, "after capture")
            return

        stage_start = time.perf_counter()
        ocr_text = ocr_image_to_text(output_path)
        _update_log_state(rid, t_ocr=_elapsed_ms(stage_start))
        print_ocr_text(ocr_text)
        if not is_current_request(rid):
            _cancel_request(rid, "after OCR")
            return

        stage_start = time.perf_counter()
        task = classify_task(ocr_text)
        _update_log_state(rid, t_vision=_elapsed_ms(stage_start))
        print(f"[vision] task={task} (rid={rid})")
        _update_log_state(rid, task=task)
        if not is_current_request(rid):
            _cancel_request(rid, "after vision")
            return

        stage_start = time.perf_counter()
        context = build_context(task, ocr_text)
        _update_log_state(rid, t_context=_elapsed_ms(stage_start))
        print_context(context)
        _update_log_state(rid, context=context)
        if not is_current_request(rid):
            _cancel_request(rid, "after context")
            return

        _debug_delay_before_suggestion(rid)
        if not is_current_request(rid):
            _cancel_request(rid, "before suggestion")
            return

        try:
            stage_start = time.perf_counter()
            result = generate_suggestion_with_metadata(context)
            _update_log_state(rid, t_llm=_elapsed_ms(stage_start))
            suggestion, model, prompt_tokens = _suggestion_parts(result)
            _update_log_state(rid, model=model, prompt_tokens=prompt_tokens)
        except Exception as exc:
            _update_log_state(rid, t_llm=_elapsed_ms(stage_start) if "stage_start" in locals() else 0)
            print(f"[suggestion] FAILED rid={rid}: {exc!r}")
            _finalize_request_log(
                rid,
                status="failed",
                cancelled_by_newer_request=False,
                error_type=type(exc).__name__,
                overlay_shown=False,
            )
            return

        if not is_current_request(rid):
            _update_log_state(rid, suggestion_present=bool(suggestion))
            _cancel_request(rid, "after suggestion")
            return

        print(f"[suggestion] begin (rid={rid})")
        if suggestion:
            print(suggestion)
        else:
            print("[suggestion] empty response")
        print(f"[suggestion] end (rid={rid})")
        _update_log_state(rid, suggestion_present=bool(suggestion))

        if not is_current_request(rid):
            _cancel_request(rid, "before overlay")
            return

        print(f"[overlay] queued rid={rid}")
        _queue_overlay(rid, task, suggestion)
    except Exception as exc:
        print(f"[pipeline] FAILED rid={rid}: {exc!r}")
        _finalize_request_log(
            rid,
            status="failed",
            cancelled_by_newer_request=False,
            error_type=type(exc).__name__,
            overlay_shown=False,
        )


def start_request() -> threading.Thread:
    """Start one request on a daemon thread and return the thread handle."""
    rid = _claim_new_request_id()
    _start_log_state(rid)
    print(f"[hotkey] new request rid={rid}")
    thread = threading.Thread(target=_run_pipeline, args=(rid,), daemon=True)
    thread.start()
    return thread


def on_hotkey() -> None:
    """Hotkey callback: claim a new request and let it supersede older ones."""
    start_request()


def main() -> None:
    print(f"[main] hotkey:  {HOTKEY}")
    print(f"[main] output:  {REPO_ROOT}/last_frame_rid_<rid>.png")
    print("[main] press the hotkey to capture, OCR, build context, suggest, and show overlay; Ctrl+C to quit.")
    print("[main] note: Step 6 validation should press one warm-up hotkey before formal A/B testing.")
    print("[main] optional validation delay: export SCREENSENSE_DEBUG_DELAY_SEC=2")
    listener = threading.Thread(target=run_hotkey_loop, args=(HOTKEY, on_hotkey), daemon=True)
    listener.start()
    run_overlay_dispatch_loop()


if __name__ == "__main__":
    main()
