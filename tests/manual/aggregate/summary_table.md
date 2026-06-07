# ScreenSense-Agent Step 8B -- N=10 close-out summary

> SCOPE GUARD: pilot evaluation, N=10 small sample. NOT a user study / NOT statistically significant / NOT submitted/published. Outcome-level working hypothesis (NOT confirmed mechanism). Mechanism-neutral: NOT attributed to any single pipeline layer (OCR / parser / context). NO first-runnable PASS claim; the internal threshold check reports FAIL.

| sample | staging | structure_class | task | context_chars | relevance | actionability | accepted |
|---|---|---|---|---|---|---|---|
| 01 | Python ImportError | structured | code_error | 1842 | 1.0 | 0.5 | True |
| 02 | shell command-not-found | non | unknown | 39 | 0.0 | 0.0 | False |
| 03 | Python ModuleNotFound (numpyy) | structured | code_error | 1842 | 1.0 | 1.0 | True |
| 04 | Python ImportError (os submodule) | structured | code_error | 1687 | 1.0 | 0.5 | True |
| 05 | git non-repo | non | unknown | 39 | 0.0 | 0.0 | False |
| 06 | LaTeX compile (l.4 locator) | structured | code_error | 1842 | 1.0 | 0.5 | True |
| 07 | LaTeX file-not-found | non | unknown | 39 | 0.0 | 0.0 | False |
| 08 | C/C++ clang undeclared-id | structured | code_error | 1146 | 1.0 | 1.0 | True |
| 09 | cat/ls file-not-found | non | unknown | 39 | 0.0 | 0.0 | False |
| 10 | JSON parse err (json.tool line/col) | semi | unknown | 39 | 0.0 | 0.0 | False |

**N=10; accepted=5; rejected=5; latency-invalid=4 (06/08/09/10).**

- structured (traceback/compiler: Python/LaTeX/C++) -> code_error + substantial context + accepted.
- semi (locator-only) + non (no locator) -> unknown + 39 chars + rejected.
- locator-only sample_10 fell to unknown in this N=10 pilot; observed outcomes are more consistent with traceback/compiler-style presentations entering code_error, but this is not a confirmed mechanism.
