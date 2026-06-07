# ScreenSense-Agent Step 8B N=10 Manual Evaluation Summary

## File Role

Close-out summary for the Step 8B N=10 manual evaluation. This is not a
paper section and not a product claim. The main analysis is the complete N=10
sample set (samples 01-10): all ten samples are scored on relevance and
actionability and are included in the aggregate metrics and the first-runnable
decision. An earlier two-view presentation (a "strict uniform-entry" view over
samples 01-09 reported in parallel with the full N=10) has been retired; the
strict 9/10 view is no longer a parallel formal result. See the Provenance /
Audit Note below for why.

## Fixed Evaluation Scope

- Scenario scope: code / terminal error scenarios only.
- Sampling mode: deliberate sampling as the main N=10 set.
- Scoring dimensions: relevance and actionability.
- No automatic scoring.
- No code, prompt, routing, OCR, overlay, or logger changes were made to improve
  any sample's model output during sampling.
- sample_10 caveat: the counted run is the 2026-06-04 normal-runtime retake; it
  is scored and included in the N=10 set like every other sample. Its
  t_render/t_total are latency-invalid (overlay window lifetime; same handling as
  06/08/09) and do not affect scoring or N=10 inclusion. See the Provenance /
  Audit Note below.

## First-Runnable Threshold

The pre-fixed first-runnable threshold is met only if all are true:

| Criterion | Required |
|---|---:|
| Average relevance score | >= 0.6 |
| Average actionability score | >= 0.4 |
| Samples with relevance_score > 0 | >= 7 / 10 |
| Samples with actionability_score > 0 | >= 5 / 10 |

## Sample List

| sample_id | scenario_type | task | context_size.chars | relevance_score | actionability_score | accepted_or_rejected | main_failure_mode / note |
|---|---|---|---:|---:|---:|---|---|
| sample_01 | Python ImportError | code_error | 1842 | 1 | 0.5 | accepted | relevant but partially actionable; context attribution drift |
| sample_02 | shell command-not-found | unknown | 39 | 0 | 0 | rejected | unknown + empty context + generic fallback |
| sample_03 | Python ModuleNotFoundError typo | code_error | 1842 | 1 | 1 | accepted | exact actionable package/import typo suggestion |
| sample_04 | Python ImportError on os submodule | code_error | 1687 | 1 | 0.5 | accepted | relevant but partially inaccurate / context drift |
| sample_05 | Git non-repo error | unknown | 39 | 0 | 0 | rejected | unknown + empty context + generic fallback |
| sample_06 | LaTeX undefined control sequence | code_error | 1842 | 1 | 0.5 | accepted | relevant; line-number hallucination; latency invalid |
| sample_07 | LaTeX file-not-found, non-structured | unknown | 39 | 0 | 0 | rejected | visible error but unknown + empty context + generic fallback |
| sample_08 | C/C++ structured compiler error | code_error | 1146 | 1 | 1 | accepted | structured compiler error handled well; latency invalid (overlay window lifetime; scoring unaffected) |
| sample_09 | cat/ls missing file | unknown | 39 | 0 | 0 | rejected | non-structured file/system error followed unknown + 39 + generic fallback; latency invalid (overlay window lifetime; scoring unaffected) |
| sample_10 | JSON line/column error | unknown | 39 | 0 | 0 | rejected | locator-only JSON parse error fell to unknown + 39 + generic fallback; counted normal-runtime retake; latency invalid (overlay window lifetime; scoring unaffected) |

## Aggregate Metrics

### N=10 (full sample set — main result)

| Metric | Value |
|---|---:|
| Total samples | 10 |
| Average relevance score | 0.50 |
| Average actionability score | 0.35 |
| relevance_score > 0 count | 5 / 10 |
| actionability_score > 0 count | 5 / 10 |
| accepted count | 5 |
| rejected count | 5 |
| unclear count | 0 |

### Retired: strict uniform-entry view (samples 01-09; historical reference only; not used as a parallel formal result)

| Metric | Value |
|---|---:|
| Total samples | 9 |
| Average relevance score | 0.56 |
| Average actionability score | 0.39 |
| relevance_score > 0 count | 5 / 9 |
| actionability_score > 0 count | 5 / 9 |
| accepted count | 5 |
| rejected count | 4 |
| unclear count | 0 |

This strict 9/10 view is retired: it is shown only as a historical reference, not
as a parallel formal result. The full N=10 set above is the single formal result.
See the Provenance / Audit Note for why it was retired.

## Provenance / Audit Note

- sample_10 had an earlier 2026-06-03 automated-equivalent attempt (overlay
  monkeypatched, t_render=0, no real runtime_log.jsonl success row); that attempt
  was superseded/discarded and is not counted in the N=10 set. The counted run is
  the 2026-06-04 normal-runtime retake: entry via `src.main.start_request()` +
  `src.main.process_next_overlay()`, a real overlay appeared (its ordinary
  click-close stalled and it was closed programmatically), and a normal
  runtime_log.jsonl success row was produced.
- sample_10's t_render=2577143 ms / t_total=2580285 ms are latency-invalid because
  the overlay close was delayed, the same handling applied to 06/08/09. This
  latency caveat affects only latency aggregation; it does not affect scoring or
  N=10 inclusion.
- The earlier "strict uniform-entry" view (samples 01-09) is retired and is no
  longer presented as a parallel formal result. Its basis for excluding sample_10
  was the discarded automated-equivalent attempt, which does not apply to the
  counted normal-runtime retake; and entry was not uniform across 01-09 either
  (e.g., sample_03 used a direct verification path, sample_05 used the hotkey).

Adopting the full N=10 set does not improve the overall first-runnable conclusion:
under the complete N=10 the system still does not meet the pre-registered global
threshold. This is a provenance correction (using the official sample set after
fixing provenance), not post-hoc sample selection or threshold tuning — no
threshold was changed, no latency-invalid sample was selectively excluded, and the
reported scores/thresholds were not altered to improve the conclusion.

Earlier superseded attempts are retained only as provenance records and are not
part of the official N=10 evaluation set.

## Scenario-Level Summary

| scenario_type | sample_count | relevance_score > 0 count | actionability_score > 0 count | notes |
|---|---:|---:|---:|---|
| Python/package error | 3 | 3 | 3 | Python traceback/import cases entered code_error and produced useful suggestions, with varying specificity. |
| shell/file/git non-structured errors | 3 | 0 | 0 | Shell, git, and file/system non-structured errors fell to unknown + 39 + generic fallback. |
| LaTeX-build/file error | 2 | 1 | 1 | Structured LaTeX `l.4` case succeeded; non-structured file-not-found failed. |
| C/C++ compiler error | 1 | 1 | 1 | `file:line:column: error` structured compiler format succeeded. |
| JSON line/column boundary | 1 | 0 | 0 | Semi-structured locator-only case fell to unknown; sample_10 has a latency-invalid overlay-close caveat. |

## Main Failure Modes

| failure_mode | count | representative_sample_ids | note |
|---|---:|---|---|
| Task classified as `unknown` | 5 | 02, 05, 07, 09, 10 | All rejected samples share unknown task label. |
| Context was too empty | 5 | 02, 05, 07, 09, 10 | All unknown samples recorded context_size.chars=39. |
| Suggestion was too generic | 5 | 02, 05, 07, 09, 10 | Generic fallback did not mention visible task. |
| Suggestion relevant but partially inaccurate | 3 | 01, 04, 06 | Accepted but actionability 0.5 due to drift or line-number issue. |
| UI/logging issue affected evaluation | 4 | 06, 08, 09, 10 | Latency invalid: t_render/t_total reflect overlay window lifetime, not trigger-to-suggestion latency; per-stage timings diagnostic-only; scoring validity unaffected. |
| Context attribution drift / contamination | 2 | 01, 04 | Relevant suggestions included non-trigger context. |
| OCR missed/noisy key text | 0 as final tag | — | Mechanism-neutral policy: visible errors missing from suggestion path were not attributed to OCR alone without source-level inspection. |

## Outcome-Level Working Hypothesis

N=10 outcome split:

- Structured / traceback-or-compiler-style errors:
  - sample_01 / 03 / 04: Python tracebacks -> code_error + substantial context + accepted
  - sample_06: LaTeX `l.4` locator -> code_error + substantial context + accepted
  - sample_08: C/C++ `file:line:column: error` -> code_error + substantial context + accepted
- Non-structured or locator-only errors:
  - sample_02 / 05 / 07 / 09 -> unknown + 39 + rejected
  - sample_10: JSON line/column only -> unknown + 39 + rejected

Working hypothesis: observed outcomes suggest higher success on structured
traceback/compiler-style error presentations than on non-structured or
locator-only terminal failures. This is an outcome-level observation only. It is
not a confirmed parser mechanism; source-level inspection is required before
claiming which layer drives the split.

## First-Runnable Decision

Decision: **FAIL**.

The decision uses the complete N=10 set (sample_10 included). The full N=10 falls
below the pre-fixed first-runnable threshold (see the table below), so the
Step 8B close-out conclusion is FAIL rather than INCONCLUSIVE. The retired strict
9/10 view (see Provenance / Audit Note) does not change this conclusion.

### N=10 threshold check (full sample set)

| Criterion | Result | Pass? |
|---|---:|---|
| Average relevance score >= 0.6 | 0.50 | No |
| Average actionability score >= 0.4 | 0.35 | No |
| At least 7/10 samples relevance_score > 0 | 5 / 10 | No |
| At least 5/10 samples actionability_score > 0 | 5 / 10 | Yes |

Decision:

```text
FAIL under the pre-fixed first-runnable threshold.
```

Short justification:

```text
The system is useful on structured code/compile errors but fails consistently
on non-structured or locator-only terminal errors. The complete N=10 set
(sample_10 included) does not meet the average relevance, average actionability,
or relevance-count thresholds. Therefore Step 8B does not support a first-runnable
PASS under the pre-fixed threshold. This is an internal evaluation result, not a
product claim.
```

### Retired: strict uniform-entry view

The earlier strict 9/10 view (samples 01-09) is retired and is not used as a
parallel formal result or as a PASS/FAIL basis. See the Provenance / Audit Note
for the reason it was retired.

## Minimal Internal Summary

- What worked: structured Python, LaTeX compile, and C/C++ compiler errors often produced task-relevant suggestions.
- Where suggestions were actionable: sample_03 and sample_08 reached full actionability; sample_01/04/06 were useful but partially inaccurate.
- Main failure pattern: unknown + 39 + generic fallback on non-structured or locator-only terminal errors.
- Boundary insight: JSON line/column locator alone did not enter code_error, while C/C++ compiler `file:line:column: error` did.
- OCR/context caveat: visible errors missing from suggestions are recorded mechanism-neutrally; no single layer is blamed without source-level inspection.
- First-runnable: Step 8B closes as FAIL under the pre-fixed threshold on the complete N=10 set (sample_10 included).
- Follow-up: close Step 8B with this failure boundary; any source-level diagnosis or retake belongs to a later, separate diagnostic phase.

## Scope Self-Check

- [x] All 10 samples are code/terminal error scenarios.
- [x] Scores use the fixed 0/0.5/1 relevance/actionability rubric.
- [x] No sample was rescored after changing the rubric.
- [x] No code or prompt changes were made to improve sample outputs during N=10 sampling.
- [x] This summary avoids paper-style claims and stays internal.
- [x] sample_10 provenance (superseded 2026-06-03 automated-equivalent attempt vs counted 2026-06-04 normal-runtime retake) and its latency-invalid caveat are explicitly preserved.
