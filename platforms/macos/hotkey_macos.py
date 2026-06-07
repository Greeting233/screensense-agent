"""macOS global hotkey wrapper.

v0 is macOS-only. Equivalent implementations for Linux / Windows should live in
platforms/<os>/<...>.py and keep the same function signature (the interface is
the function-signature contract, not an abstract base class).

Permissions: on first run, macOS requires granting Accessibility and Screen
Recording permissions in System Settings (see the root README).
"""
from typing import Callable

from pynput import keyboard


def run_hotkey_loop(combo: str, on_trigger: Callable[[], None]) -> None:
    """Block and listen for a global hotkey until the process is terminated (Ctrl+C).

    Args:
        combo: pynput combo syntax, e.g. '<ctrl>+<alt>+s'.
        on_trigger: callback invoked on hotkey press; no args, no return value.
    """
    with keyboard.GlobalHotKeys({combo: on_trigger}) as h:
        h.join()
