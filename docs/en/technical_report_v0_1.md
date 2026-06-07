# ScreenSense-Agent v0.1 — Technical Report

> **Scope & status.** This is an internal **v0.1 pilot evaluation** report. It is **not** a user study, is **not** statistically significant, and has **not** been submitted or published. Findings are stated at the **outcome level** and are **mechanism-neutral**: no single pipeline stage (OCR / parser / context) is claimed as a cause without source-level inspection. All numbers are reported as measured; nothing is recomputed.

## Abstract

ScreenSense-Agent (SSA) is a **suggestion-first**, low-latency screen-aware research system. From a single desktop screenshot it runs an **observe–parse–suggest–wait** pipeline and, under explicit latency constraints, produces **one** short task-relevant suggestion. It does **not** click, type, or take over the keyboard or mouse, and it is **not** an autonomous desktop agent or a computer controller.

This report covers the N=10 pilot manual evaluation of SSA's first-runnable scenario — **code / terminal error assistance**. Under four global first-runnable criteria that were fixed before sampling, the complete N=10 set scores: average relevance **0.50**, average actionability **0.35**, relevance > 0 in **5/10** samples, actionability > 0 in **5/10** samples (three of the four criteria are not met and one is just met, so the pre-registered global threshold is **not** met). Alongside this, the pilot reveals a stable outcome-level boundary: **structured / traceback- or compiler-style** errors tend to enter `code_error` with substantial context and be accepted, while **non-structured or weakly-structured (locator-only)** terminal/file errors fall to `unknown` with minimal context and a generic fallback, and are rejected. The structured / non-structured split is descriptive within this N=10 pilot and is not a confirmed mechanism or a general performance law.

---

## 1. Project Overview

### 1.1 Positioning

SSA is a research system that studies **how much context must be extracted from a single desktop frame to produce a useful suggestion**, treating context construction as a measurable system variable. It is explicitly **not** a general desktop system layer, **not** an autonomous agent, and **not** a productivity overlay.

The system holds a strict **suggestion-first** boundary: it only observes, parses, and suggests, then waits for the user; the user keeps full control at all times. Out of scope by design: automatic clicking, automatic typing, keyboard/mouse takeover, permission bypass, game assistance, and account automation. The suggestion prompt itself instructs the model to keep the user in full control and not to suggest automatic clicking or typing. The behavior contract in one phrase: **observe-parse-suggest-wait**.

### 1.2 Research Questions

Overall question: under suggestion-first constraints, what is the **minimum effective context** to extract from a single desktop frame, and how do context cost, suggestion relevance, and end-to-end latency trade off? It decomposes into four sub-questions:

- **RQ1 — Task discrimination.** Can a rule-based engine, using only window metadata + full-frame OCR, reliably identify the task class?
- **RQ2 — Minimum effective context.** For a given task, how does suggestion relevance change as context is extended from a minimal set to richer sets, and where is the diminishing-returns point?
- **RQ3 — System cost distribution.** Which stage dominates end-to-end latency and resource cost, and does that shift with context size?
- **RQ4 — Upgrade triggers.** Under what measurable conditions does the minimal system stop being sufficient (rules → vision LLM; single cloud call → routing; single frame → temporal window)?

RQ1 is the entry point, RQ2 is the center, RQ3 is the system analysis, and RQ4 is the upgrade discipline.

### 1.3 First-Runnable Scenario

The first-runnable scenario is **code / terminal error assistance**. It was chosen **not** as a product demo, but as the first real-world desktop task used to validate the end-to-end "task discrimination → context extraction → suggestion generation" pipeline: error text is dense, suggestion relevance is easy for a human to judge, and the scenario naturally supports minimum-context ablation (the starting point for RQ2). This report covers the N=10 evaluation of this first-runnable scenario.

---

## 2. System Pipeline

### 2.1 Shape

The v0 pipeline is a **single-shot** system chain: one hotkey press triggers one full pipeline run; when the run ends the system goes quiet, keeps no durable session state across runs, and pre-triggers no follow-up action. Characteristics:

- **Invocation:** hotkey → one full pipeline run.
- **Concurrency:** serial in the implementation (see §2.3).
- **Streaming:** none.
- **Event-driven:** no; only explicit hotkey triggering.
- **Cancellation:** when a newer hotkey arrives, the **newer request supersedes the older one** — a stale in-flight request no longer updates the visible overlay.
- **Persistent state:** limited to an in-memory previous-context slot; the system does not maintain a multi-turn desktop session.

### 2.2 Pipeline Chain

```text
hotkey → screen capture (mss) → OCR (Tesseract) → rule-based task tag
→ context construction → cloud LLM → read-only overlay (macOS) → cancel rule
→ per-call JSONL log
```

The overlay is a **read-only** display window with no automatic action. The logger is cross-cutting: it writes one request-level JSON record per run.

### 2.3 Stages and Implementation

The pipeline is implemented in the `src/` modules. Stages run serially (task discrimination consumes the OCR text, so capture → OCR → task tag → context is a serial order). Each stage is timed independently:

| Stage | Implementation module | Timing field |
|---|---|---|
| Screen capture | `src/capture.py` | `t_capture` |
| OCR | `src/ocr.py` | `t_ocr` |
| Task discrimination (rule-based task tag) | `src/vision.py` | `t_vision` |
| Context construction | `src/context.py` | `t_context` |
| Suggestion generation (cloud LLM) | `src/suggestion.py` | `t_llm` |
| Overlay display (read-only) | `src/overlay.py` | `t_render` |
| Per-call logging | `src/logger.py` | `t_total`, etc. |
| Cancel rule | `src/main.py` | — |

The serial chain (capture → OCR → task tag → context → suggestion → overlay) in `src/main.py` is the basis for what actually ran during the N=10 evaluation.

---

## 3. Evaluation Protocol

### 3.1 Scope and Method

- **Type:** manual N=10 evaluation; no automatic scoring.
- **Scenario scope:** code / terminal error scenarios only.
- **Sampling mode:** deliberate sampling as the main set.
- **Scoring dimensions:** relevance and actionability, scored by a human, each in `{0, 0.5, 1}`; plus an accepted / rejected label.
- **Discipline:** during collection of the ten samples, **no** changes were made to code, prompt, OCR rules, model routing, overlay UI, or logger fields; any problem found was recorded as a failure mode rather than fixed mid-evaluation.

### 3.2 The Four Pre-Registered Global First-Runnable Criteria

The first-runnable threshold is met **only if all** of the following hold:

```text
- Average relevance score >= 0.6
- Average actionability score >= 0.4
- At least 7/10 samples have relevance_score > 0
- At least 5/10 samples have actionability_score > 0
```

This is an internal unlock threshold, not a paper claim. It is a **whole-set pass/fail judgment** over the full N=10 (two averages plus two positive-count criteria) and is a different layer from the per-sample task expectation (each sample is expected to be `code_error` or `unknown`); the two should not be conflated.

### 3.3 Pre-Registration

The four criteria were fixed and version-controlled **before the first sample was collected** — roughly **1.4 days** before the first sample's capture timestamp — and remained a **single, unchanged version** throughout sampling (no alternative threshold values appear anywhere in the project history). Fixing the criteria before sampling is a deliberate guard against confirmation bias.

### 3.4 Structure Classification

Each sample is classified by the structural form of the on-screen error:

- **structured** — a traceback- or compiler-style error carrying a parseable locator (e.g., a Python traceback, a LaTeX `l.4` locator line, or a C/C++ `file:line:column: error`).
- **semi** — a locator-only message without traceback/compiler structure (e.g., a JSON `line N column M` parse error).
- **non** — no structured locator (e.g., shell command-not-found, git non-repository error, or a file-not-found error).

At the outcome level: structured errors tended to enter `code_error` with substantial context and be accepted; semi (locator-only) and non (no locator) errors tended to fall to `unknown` with minimal context and be rejected. A semi case (a JSON line/column locator without traceback/compiler structure) fell to `unknown`, which narrows the working hypothesis toward "traceback/compiler-style structure" rather than "any locator".

---

## 4. N=10 Results

### 4.1 Per-Sample Results

| sample | structure_class | task | context chars | relevance | actionability | accept/reject |
|---|---|---|---:|---:|---:|---|
| sample_01 | structured | code_error | 1842 | 1.0 | 0.5 | accepted |
| sample_02 | non | unknown | 39 | 0.0 | 0.0 | rejected |
| sample_03 | structured | code_error | 1842 | 1.0 | 1.0 | accepted |
| sample_04 | structured | code_error | 1687 | 1.0 | 0.5 | accepted |
| sample_05 | non | unknown | 39 | 0.0 | 0.0 | rejected |
| sample_06 | structured | code_error | 1842 | 1.0 | 0.5 | accepted |
| sample_07 | non | unknown | 39 | 0.0 | 0.0 | rejected |
| sample_08 | structured | code_error | 1146 | 1.0 | 1.0 | accepted |
| sample_09 | non | unknown | 39 | 0.0 | 0.0 | rejected |
| sample_10 | semi | unknown | 39 | 0.0 | 0.0 | rejected |

Totals: N=10; accepted = 5; rejected = 5; latency-invalid = 4 (samples 06, 08, 09, 10 — see §4.3).

### 4.2 Aggregate Metrics

**N=10 (full sample set — main result):**

| Metric | Value |
|---|---:|
| Total samples | 10 |
| Average relevance score | 0.50 |
| Average actionability score | 0.35 |
| relevance_score > 0 count | 5 / 10 |
| actionability_score > 0 count | 5 / 10 |
| accepted count | 5 |
| rejected count | 5 |

**Retired: strict uniform-entry view (samples 01-09; historical reference only; not used as a parallel formal result):**

| Metric | Value |
|---|---:|
| Total samples | 9 |
| Average relevance score | 0.56 |
| Average actionability score | 0.39 |
| relevance_score > 0 count | 5 / 9 |
| actionability_score > 0 count | 5 / 9 |

An earlier two-view presentation (a "strict uniform-entry" 9/10 view reported in parallel with the full N=10) has been **retired**: the strict 9/10 view is shown here as a historical reference only and is **not used as a parallel formal result**. The complete N=10 set is the single formal result. See §4.3 for why it was retired.

### 4.3 Provenance / Audit Note

- **sample_10 provenance.** An earlier attempt at sample_10 used an automated-equivalent overlay (the overlay function was patched to return immediately, so its render time was zero and no normal runtime log row was produced). That attempt was **superseded/discarded and is not counted**. The counted run is the **normal-runtime retake**: it entered through the normal runtime entry path, a real overlay was shown, its ordinary click-close stalled and it was closed programmatically, and it produced a normal per-call log row.
- **sample_10 latency.** Its `t_render = 2577143 ms` / `t_total = 2580285 ms` are **latency-invalid** because the overlay close was delayed (the window stayed open before programmatic closure); these reflect overlay window lifetime, not trigger-to-suggestion latency. This is the **same handling** applied to samples 06, 08, and 09. The latency caveat affects only latency aggregation; it does **not** affect scoring or N=10 inclusion. Per-stage capture/OCR/LLM timings are retained as diagnostic-only.
- **Retired strict view.** The earlier strict uniform-entry view (samples 01-09) is retired and is no longer presented as a parallel formal result. Its basis for excluding sample_10 was the discarded automated-equivalent attempt, which does not apply to the counted normal-runtime retake; and entry was not uniform across 01-09 either.

Adopting the full N=10 set does **not** improve the overall first-runnable conclusion: under the complete N=10 the system still does not meet the pre-registered global threshold. This is a **provenance correction** (using the official sample set after fixing provenance), **not** post-hoc sample selection or threshold tuning — no threshold was changed, no latency-invalid sample was selectively excluded, and the reported scores/thresholds were not altered to improve the conclusion.

Earlier superseded attempts are retained only as provenance records and are not part of the official N=10 evaluation set.

---

## 5. Failure Boundary Finding (outcome-level only; mechanism-neutral)

### 5.1 Observed Outcome Split

Split by structure class, the N=10 outcomes show a clean two-way pattern:

- **structured (samples 01 / 03 / 04 / 06 / 08 — 5 of 5):** `code_error` + substantial context (1146–1842 chars) + **all accepted**. These are Python tracebacks (01 / 03 / 04), a LaTeX `l.4` locator (06), and a C/C++ `file:line:column: error` (08).
- **non + semi (samples 02 / 05 / 07 / 09 / 10 — 5 of 5):** `unknown` + a minimal 39-char context + **all rejected**. These are shell command-not-found (02), git non-repository (05), LaTeX file-not-found (07), cat/ls missing file (09), and a JSON line/column locator (10).

Boundary detail: a C/C++ compiler `file:line:column: error` entered `code_error`, whereas a JSON line/column locator alone did **not** enter `code_error`.

### 5.2 Working Hypothesis (mechanism-neutral)

Observed outcomes **suggest** higher success on structured traceback/compiler-style error presentations than on non-structured or locator-only terminal failures. This is an **outcome-level observation only**. It is **not** a confirmed parser mechanism; source-level inspection is required before claiming which layer drives the split. No single pipeline layer (OCR / parser / context) is attributed as the cause. The structured / non-structured split is descriptive within this N=10 pilot and is not a confirmed mechanism or a general performance law.

---

## 6. Limitations & Next Steps

### 6.1 Limitations

- **Pilot scale.** N=10 deliberate sampling — **not** a user study, **not** statistically significant, **not** submitted or published.
- **Latency validity.** Four of ten samples (06, 08, 09, 10) are latency-invalid because their overlay close was delayed, so their `t_render` / `t_total` reflect overlay window lifetime rather than real end-to-end latency. Per-stage timings are diagnostic-only; scoring is unaffected.
- **Mechanism-neutral.** No source-level attribution was performed; the structured / non-structured split is an outcome-level observation, not attributed to any pipeline layer.
- **Scenario scope.** Conclusions are limited to the code / terminal error first-runnable scenario and are not extrapolated to other desktop tasks.

### 6.2 Next Steps

- **Source-level diagnosis** of the structured-vs-non-structured split (which layer drives it) belongs to a later, separate diagnostic phase; this report draws no mechanism conclusion.
- **Minimum-effective-context ablation (RQ2):** on the first-runnable scenario, vary context from a minimal set to richer sets and measure the relevance knee point. A planned extension compares four context baselines (full OCR / rule-filtered / minimal-oracle / no-context).
- **Broader scenarios:** extend beyond code / terminal errors only after the first-runnable scenario is well characterized.

---

## First-Runnable Verdict

**Threshold vs. measured (full N=10):**

| Criterion | Required | Measured (full N=10) | Met? |
|---|---:|---:|---|
| Average relevance score | >= 0.6 | 0.50 | No |
| Average actionability score | >= 0.4 | 0.35 | No |
| Samples with relevance_score > 0 | >= 7 / 10 | 5 / 10 | No |
| Samples with actionability_score > 0 | >= 5 / 10 | 5 / 10 | Yes |

Three of the four criteria are not met; one is just met.

**Verdict.**

> Under the pre-registered global first-runnable threshold, SSA v0.1 does **not** pass as a general code/terminal error assistant (3 of 4 criteria not met; 1 just met). However, within this N=10 pilot it reveals a **stable outcome-level boundary**: structured / traceback-like errors consistently enter `code_error` + substantial-context + accepted, while non-structured or weakly-structured terminal/file errors fall to `unknown` + minimal-context + generic fallback.

- **Supporting evidence (the structured/non-structured split).** Structured samples (01 / 03 / 04 / 06 / 08) were 5/5 accepted; non + semi samples (02 / 05 / 07 / 09 / 10) were 5/5 rejected. **Risk note:** the structured subset is only 5 samples — this is **not** stated as a PASS and is **not** generalized beyond the sample.
- **Qualifier 1 (mechanism-neutral).** This boundary is an outcome-level observation within the pilot; no single pipeline layer (OCR / parser / context) is claimed as its cause, and source-level inspection is required before any such attribution (not a confirmed mechanism).
- **Qualifier 2 (scope).** All boundary statements are scoped as "within this N=10 pilot ... consistently ..."; they are not claims of general stability beyond the sample. The result is an internal pilot evaluation — not a user study, not statistically significant, not submitted or published.

The structured / non-structured split is descriptive within this N=10 pilot and is not a confirmed mechanism or a general performance law.
