# ScreenSense-Agent

**A research system for low-latency desktop context extraction and task-relevant suggestion generation in real-world tasks.**

ScreenSense-Agent (SSA) studies a desktop pipeline that starts from a single screen frame, performs task discrimination, constructs a **minimum effective context**, and generates one short, task-relevant suggestion under explicit latency constraints. It treats context construction as a measurable system variable.

It is **suggestion-first**: it only **observes → parses → suggests → waits**. The user keeps full control at all times. SSA is **not** an autonomous desktop agent, **not** a computer controller, and **not** a productivity overlay. The overlay is only a read-only output surface for showing a suggestion; it is not a productivity-overlay product or a desktop control layer.

## Boundary (out of scope by design)

- No automatic clicking
- No automatic typing
- No keyboard / mouse takeover
- No permission bypass
- No game assistance
- No account automation

The suggestion prompt itself instructs the model to keep the user in full control and not to suggest automatic clicking or typing.

## Research question

Under suggestion-first constraints, what is the **minimum effective context** to extract from a single desktop frame, and how do context cost, suggestion relevance, and end-to-end latency trade off across real-world tasks? It decomposes into:

1. **Task discrimination** — can rule-based parsing of window metadata + full-frame OCR reliably identify the task class?
2. **Minimum effective context** — how does suggestion relevance change as context is extended from a minimal set to richer sets? Where is the diminishing-returns point?
3. **System cost distribution** — which pipeline stage dominates end-to-end latency and resource cost?
4. **Upgrade triggers** — under what measured conditions does the minimal system stop being sufficient?

## Pipeline

Single-shot, hotkey-triggered, single-frame:

```text
hotkey → screen capture (mss) → OCR (Tesseract) → rule-based task tag
→ context construction → cloud LLM → read-only overlay (macOS) → cancel rule
→ per-call JSON log
```

The implementation lives in [`src/`](src/): `capture`, `ocr`, `vision` (rule-based task tag), `context`, `suggestion`, `overlay`, `logger`, `main`.

## How to run locally

This is a research proof-of-concept (macOS, single-shot hotkey pipeline).

```bash
# 1. Install (Python 3.11+; Tesseract must be installed on the system)
pip install -e .

# 2. Provide your own cloud LLM credentials (never commit a key)
export OPENAI_API_KEY=...        # read from your environment; not stored in the repo

# 3. (optional) Choose the model
export SCREENSENSE_MODEL=...      # The default model can be overridden with SCREENSENSE_MODEL;
                                  # use a model available in your own API account.

# 4. Run (macOS needs Screen Recording + Accessibility permissions for the hotkey)
bash scripts/run_dev.sh          # equivalent to: python -m src.main
```

## Evaluation snapshot (v0.1 pilot — completed)

The first-runnable scenario is **code / terminal error assistance**. A small **N=10 pilot manual evaluation** was completed and scored on relevance and actionability against four global criteria fixed before sampling.

**Result:** under the pre-registered global threshold, the complete N=10 set does **not** pass (average relevance 0.50, average actionability 0.35, relevance>0 in 5/10, actionability>0 in 5/10 — three of four criteria not met, one just met). Alongside this, the pilot **observed a consistent outcome-level boundary within this N=10 pilot**: structured / traceback- or compiler-style errors tended to enter `code_error` with substantial context and be accepted, while non-structured or weakly-structured terminal/file errors fell to `unknown` with minimal context and a generic fallback.

This is an internal pilot evaluation — **not** a user study, **not** statistically significant, **not** a confirmed mechanism or general performance law. Details:

- Technical report: [`docs/en/technical_report_v0_1.md`](docs/en/technical_report_v0_1.md)
- N=10 summary: [`tests/manual/n10_summary.md`](tests/manual/n10_summary.md)
- Aggregate table + figures: [`tests/manual/aggregate/`](tests/manual/aggregate/)

> Note: per-sample raw screenshots and logs are intentionally **not** included — they can contain real on-screen content. Only the aggregate summary and figures are published.

## License

MIT — see [LICENSE](LICENSE).
