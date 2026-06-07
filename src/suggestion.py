"""Step 4 - first task-relevant suggestion to stdout.

Single cloud LLM call only. No overlay, logger, retry, cache, fallback, routing,
streaming, memory, or prompt template engine.
"""
from __future__ import annotations

from dataclasses import dataclass
import os

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.4-mini"


@dataclass(frozen=True)
class SuggestionResult:
    """LLM suggestion plus minimal metadata needed by Step 7 logging."""

    text: str
    model: str
    prompt_tokens: int | None


def build_prompt(context: dict[str, str]) -> str:
    """Build the smallest prompt needed for a short task-relevant suggestion."""
    return f"""You are part of a suggestion-first desktop pipeline.
The user keeps full control. Do not suggest automatic clicking or typing.

Task label: {context.get("task", "unknown")}

Terminal text:
{context.get("terminal_text", "")}

Editor text excerpt:
{context.get("editor_text_excerpt", "")}

Return one short, task-relevant suggestion in 2-4 lines.
If the task is unknown or the context is unclear, say what to check next.
"""


def current_model_name() -> str:
    """Return the configured model name for this request."""
    return os.environ.get("SCREENSENSE_MODEL", DEFAULT_MODEL)


def _usage_value(usage: object, *names: str) -> int | None:
    """Read a token count from either an SDK object or a dict."""
    for name in names:
        value = None
        if isinstance(usage, dict):
            value = usage.get(name)
        else:
            value = getattr(usage, name, None)
        if isinstance(value, int):
            return value
    return None


def _prompt_tokens_from_response(response: object) -> int | None:
    """Extract prompt/input token count when the SDK exposes usage metadata."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    return _usage_value(usage, "input_tokens", "prompt_tokens")


def generate_suggestion_with_metadata(context: dict[str, str]) -> SuggestionResult:
    """Call one cloud model once and return suggestion text plus metadata."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI()
    model = current_model_name()
    response = client.responses.create(
        model=model,
        input=build_prompt(context),
    )
    actual_model = getattr(response, "model", None) or model
    return SuggestionResult(
        text=response.output_text.strip(),
        model=str(actual_model),
        prompt_tokens=_prompt_tokens_from_response(response),
    )


def generate_suggestion(context: dict[str, str]) -> str:
    """Call one cloud model once and return the suggestion text."""
    return generate_suggestion_with_metadata(context).text


def print_suggestion(context: dict[str, str]) -> str | None:
    """Print the LLM suggestion in a visible stdout block."""
    print("[suggestion] begin")
    try:
        suggestion = generate_suggestion(context)
    except Exception as exc:
        print(f"[suggestion] FAILED: {exc!r}")
        print("[suggestion] end")
        return None

    if suggestion:
        print(suggestion)
    else:
        print("[suggestion] empty response")
    print("[suggestion] end")
    return suggestion or None
