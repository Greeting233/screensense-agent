"""Step 1 — single-frame capture.

Grab one frame of the primary screen and write it to PNG. Dumb-but-runnable:
no post-processing, no burst capture, no recording, no multi-monitor stitching.
"""
from pathlib import Path

import mss
import mss.tools


def capture_to_path(path: Path) -> None:
    """Grab one frame of the primary screen and save it as PNG.

    Args:
        path: Output PNG path. The parent directory must already exist.

    Notes:
        mss.monitors[0] is the virtual screen spanning all displays;
        monitors[1] is the primary display. v0 captures the primary display
        only; multi-monitor stitching is explicitly out of scope.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sshot = sct.grab(monitor)
        mss.tools.to_png(sshot.rgb, sshot.size, output=str(path))
