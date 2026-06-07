"""Step 3 - rule-based task parsing.

Minimal rules only. This is not visual understanding, not a vision LLM, and not
layout analysis. The parser receives OCR text and returns one task label.
"""

CODE_ERROR_KEYWORDS = (
    "traceback",
    "syntaxerror",
    "typeerror",
    "valueerror",
    "importerror",
    "modulenotfounderror",
    "exception",
    "error:",
    "failed tests",
    "pytest",
    "npm err",
    "command not found",
)

INSTALL_ERROR_KEYWORDS = (
    "brew install",
    "pip install",
    "npm install",
    "installation failed",
    "installer",
    "permission denied",
    "could not install",
    "package not found",
    "dependency",
)


def classify_task(ocr_text: str) -> str:
    """Classify the current task with small keyword rules."""
    lowered = ocr_text.lower()

    if any(keyword in lowered for keyword in CODE_ERROR_KEYWORDS):
        return "code_error"
    if any(keyword in lowered for keyword in INSTALL_ERROR_KEYWORDS):
        return "install_error"
    return "unknown"
