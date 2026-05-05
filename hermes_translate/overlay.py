"""
Minimal macOS floating panel — just translated text, dark bg, auto-size.
"""

import threading
from typing import Optional

import objc
from AppKit import (
    NSApp, NSApplication, NSApplicationActivationPolicyAccessory,
    NSPanel, NSBackingStoreBuffered,
    NSTextField,
    NSColor, NSFont, NSString,
    NSBorderlessWindowMask, NSNonactivatingPanelMask,
    NSUtilityWindowMask,
    NSFloatingWindowLevel, NSScreen,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorFullScreenAuxiliary,
    NSWindowCollectionBehaviorStationary,
    NSTimer,
    NSFontAttributeName, NSStringDrawingUsesLineFragmentOrigin,
)
from Foundation import NSObject, NSMakeRect, NSPoint, NSMakeSize

PAD = 14
FONT_SIZE = 15
AUTO_DISMISS = 4.0
MAX_WIDTH = 560


def _measure(text: str, font: NSFont) -> tuple:
    ns = NSString.stringWithString_(text)
    single = ns.sizeWithAttributes_({NSFontAttributeName: font})
    w = min(max(single.width, 60), MAX_WIDTH - PAD * 2)
    rect = ns.boundingRectWithSize_options_attributes_(
        NSMakeSize(w, 10000), NSStringDrawingUsesLineFragmentOrigin,
        {NSFontAttributeName: font},
    )
    return round(rect.size.width) + 8, round(rect.size.height) + 4


class SimplePanel:
    """Single NSPanel showing just translation text."""

    def __init__(self, text: str, on_dismiss=None):
        self.on_dismiss = on_dismiss
        self.panel = None
        self._timer = None
        self._field = None
        self._build(text)

    def _build(self, text: str):
        NSApplication.sharedApplication().setActivationPolicy_(
            NSApplicationActivationPolicyAccessory
        )
        font = NSFont.systemFontOfSize_(FONT_SIZE)
        tw, th = _measure(text, font)
        pw = tw + PAD * 2
        ph = th + PAD * 2

        frame = NSMakeRect(0, 0, pw, ph)
        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSBorderlessWindowMask | NSNonactivatingPanelMask | NSUtilityWindowMask,
            NSBackingStoreBuffered, False,
        )
        self.panel.setLevel_(NSFloatingWindowLevel)
        self.panel.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorFullScreenAuxiliary
            | NSWindowCollectionBehaviorStationary
        )
        self.panel.setOpaque_(False)
        self.panel.setBackgroundColor_(NSColor.clearColor())
        self.panel.setHasShadow_(True)
        self.panel.setReleasedWhenClosed_(False)

        # Dark solid background
        content = self.panel.contentView()
        content.setWantsLayer_(True)
        content.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.08, 0.08, 0.10, 0.94).CGColor()
        )
        content.layer().setCornerRadius_(10)
        content.layer().setMasksToBounds_(True)

        # Text field
        self._field = NSTextField.alloc().initWithFrame_(
            NSMakeRect(PAD, PAD, tw, th)
        )
        self._field.setStringValue_(text)
        self._field.setBezeled_(False)
        self._field.setDrawsBackground_(False)
        self._field.setTextColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.94, 0.95, 0.97, 1.0)
        )
        self._field.setFont_(font)
        self._field.setEditable_(False)
        self._field.setSelectable_(True)
        self._field.setLineBreakMode_(0)
        content.addSubview_(self._field)

        self._position()
        self._timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            AUTO_DISMISS, self, 'dismiss:', None, False
        )
        self.panel.makeKeyAndOrderFront_(None)

    def update_text(self, text: str):
        """Replace text and resize if needed."""
        if not self._field or not self.panel:
            return
        font = NSFont.systemFontOfSize_(FONT_SIZE)
        tw, th = _measure(text, font)
        pw = tw + PAD * 2
        ph = th + PAD * 2

        self._field.setStringValue_(text)
        self._field.setFrame_(NSMakeRect(PAD, PAD, tw, th))

        cur = self.panel.frame()
        if abs(cur.size.width - pw) > 4 or abs(cur.size.height - ph) > 4:
            self.panel.setFrame_display_animate_(
                NSMakeRect(cur.origin.x, cur.origin.y - (ph - cur.size.height), pw, ph),
                True, True,
            )

    def dismiss_(self, timer):
        if self.panel:
            self.panel.close()
            self.panel = None
            if self.on_dismiss:
                self.on_dismiss()

    def _position(self):
        from Quartz import CGEventCreate, CGEventGetLocation
        e = CGEventCreate(None)
        m = CGEventGetLocation(e)
        s = self.panel.frame().size
        screens = NSScreen.screens()
        sf = screens[0].frame()
        for scr in screens:
            f = scr.frame()
            if f.origin.x <= m.x <= f.origin.x + f.size.width and \
               f.origin.y <= m.y <= f.origin.y + f.size.height:
                sf = f
                break
        x = min(max(m.x - s.width / 2, sf.origin.x + 8),
                sf.origin.x + sf.size.width - s.width - 8)
        y = m.y + 8      # tight to cursor (selection area)
        if y + s.height > sf.origin.y + sf.size.height:
            y = m.y - s.height - 12
        if y < sf.origin.y:
            y = sf.origin.y + 8
        self.panel.setFrameOrigin_(NSPoint(x, y))

    def close(self):
        if self._timer:
            self._timer.invalidate()
        if self.panel:
            self.panel.close()


# ─── Global state for async update ───────────────────────────────
_panel = None
_lock = threading.Lock()
_dismissed = False


def show_loading(text: str):
    """Show loading panel immediately."""
    global _panel, _dismissed
    with _lock:
        if _panel:
            try:
                _panel.close()
            except Exception:
                pass
        _dismissed = False
        _panel = SimplePanel(text="…", on_dismiss=lambda: _set_dismissed())


def _set_dismissed():
    global _dismissed, _panel
    _dismissed = True
    _panel = None


def is_dismissed():
    return _dismissed


def update_translation(text: str):
    """Update panel with translation result."""
    global _panel
    with _lock:
        if _panel:
            try:
                _panel.update_text(text)
            except Exception:
                pass


def run_loop():
    """Block until panel dismissed."""
    app = NSApplication.sharedApplication()
    app.activateIgnoringOtherApps_(True)
    from AppKit import NSDate, NSDefaultRunLoopMode
    while not _dismissed.is_set():
        app.nextEventMatchingMask_untilDate_inMode_dequeue_(
            0xFFFFFFFF, NSDate.dateWithTimeIntervalSinceNow_(0.05),
            NSDefaultRunLoopMode, True,
        )
    with _lock:
        global _panel
        _panel = None
