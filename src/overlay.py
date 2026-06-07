"""Step 5 - readable output overlay.

Show the Step 4 suggestion in a minimal, human-readable macOS window.
No theme system, animation, drag memory, auto-dismiss policy, logger, or cancel
rule is implemented here.
"""
from __future__ import annotations

from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSBackingStoreBuffered,
    NSButton,
    NSColor,
    NSFloatingWindowLevel,
    NSMakeRect,
    NSPasteboard,
    NSPasteboardTypeString,
    NSScrollView,
    NSTextField,
    NSTextView,
    NSView,
    NSWindow,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskUtilityWindow,
    NSScreen,
)
from Foundation import NSObject
import objc


OVERLAY_WIDTH = 380
OVERLAY_HEIGHT = 240
SCREEN_MARGIN = 24

_CONTROLLERS = []


class OverlayController(NSObject):
    """Small Cocoa target/delegate object retained for the window lifetime."""

    def init(self):
        self = objc.super(OverlayController, self).init()
        if self is None:
            return None
        self.window = None
        self.suggestion = ""
        return self

    def copy_(self, _sender) -> None:
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setString_forType_(self.suggestion, NSPasteboardTypeString)

    def close_(self, _sender) -> None:
        if self.window is not None:
            self.window.close()

    def windowWillClose_(self, _notification) -> None:
        app = NSApplication.sharedApplication()
        app.stop_(None)


def _place_top_right() -> tuple[float, float]:
    screen = NSScreen.mainScreen()
    if screen is None:
        return 80.0, 80.0
    frame = screen.visibleFrame()
    x = frame.origin.x + frame.size.width - OVERLAY_WIDTH - SCREEN_MARGIN
    y = frame.origin.y + frame.size.height - OVERLAY_HEIGHT - SCREEN_MARGIN
    return x, y


def _make_label(text: str, frame) -> NSTextField:
    label = NSTextField.alloc().initWithFrame_(frame)
    label.setStringValue_(text)
    label.setBezeled_(False)
    label.setDrawsBackground_(False)
    label.setEditable_(False)
    label.setSelectable_(False)
    label.setTextColor_(NSColor.secondaryLabelColor())
    return label


def _make_button(title: str, frame, target: OverlayController, action: str) -> NSButton:
    button = NSButton.alloc().initWithFrame_(frame)
    button.setTitle_(title)
    button.setBezelStyle_(1)
    button.setTarget_(target)
    button.setAction_(action)
    return button


def show_overlay(task: str, suggestion: str) -> None:
    """Block until the user closes the single-shot overlay window."""
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    x, y = _place_top_right()
    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(x, y, OVERLAY_WIDTH, OVERLAY_HEIGHT),
        NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskUtilityWindow,
        NSBackingStoreBuffered,
        False,
    )
    window.setTitle_("ScreenSense")
    window.setLevel_(NSFloatingWindowLevel)
    window.setReleasedWhenClosed_(False)
    window.setBackgroundColor_(NSColor.windowBackgroundColor())

    controller = OverlayController.alloc().init()
    controller.window = window
    controller.suggestion = suggestion
    _CONTROLLERS.append(controller)
    window.setDelegate_(controller)

    content = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, OVERLAY_WIDTH, OVERLAY_HEIGHT))
    window.setContentView_(content)

    task_label = _make_label(f"task: {task}", NSMakeRect(14, OVERLAY_HEIGHT - 32, 260, 18))
    content.addSubview_(task_label)

    scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(14, 52, OVERLAY_WIDTH - 28, 142))
    scroll.setHasVerticalScroller_(True)
    scroll.setBorderType_(0)
    text_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, OVERLAY_WIDTH - 44, 142))
    text_view.setString_(suggestion)
    text_view.setEditable_(False)
    text_view.setSelectable_(True)
    text_view.setDrawsBackground_(False)
    scroll.setDocumentView_(text_view)
    content.addSubview_(scroll)

    copy_button = _make_button(
        "Copy",
        NSMakeRect(OVERLAY_WIDTH - 178, 14, 78, 28),
        controller,
        "copy:",
    )
    close_button = _make_button(
        "Close",
        NSMakeRect(OVERLAY_WIDTH - 92, 14, 78, 28),
        controller,
        "close:",
    )
    content.addSubview_(copy_button)
    content.addSubview_(close_button)

    window.makeKeyAndOrderFront_(None)
    app.activateIgnoringOtherApps_(True)
    app.run()
