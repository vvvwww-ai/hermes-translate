"""
Global hotkey listener using pynput.
Listens for the configured hotkey and triggers translation callback.
"""

import threading
from typing import Callable, Optional


class HotkeyListener:
    """Global keyboard shortcut listener."""

    def __init__(self, hotkey: str = "cmd+shift+t"):
        """
        Initialize hotkey listener.
        
        Args:
            hotkey: Hotkey string like 'cmd+shift+t', 'ctrl+alt+z'
        """
        self.hotkey = hotkey
        self._callback: Optional[Callable] = None
        self._listener = None
        self._thread: Optional[threading.Thread] = None

    def start(self, callback: Callable):
        """
        Start listening in a background thread.
        
        Args:
            callback: Function to call when hotkey is pressed.
        """
        self._callback = callback

        from pynput import keyboard

        # Parse hotkey string into pynput format
        key_combo = self._parse_hotkey(self.hotkey)

        current_keys = set()

        def on_press(key):
            try:
                # Normalize key representation
                kn = self._key_name(key)
                current_keys.add(kn)

                if key_combo.issubset(current_keys):
                    # All required keys pressed → trigger
                    # Debounce: only fire once per press sequence
                    if len(current_keys) == len(key_combo):
                        self._fire()
            except Exception:
                pass

        def on_release(key):
            try:
                kn = self._key_name(key)
                current_keys.discard(kn)
            except Exception:
                pass

        self._listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release,
        )

        self._thread = threading.Thread(target=self._listener.start, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the hotkey listener."""
        if self._listener:
            self._listener.stop()

    def _fire(self):
        """Trigger the callback in a background thread."""
        if self._callback:
            t = threading.Thread(target=self._callback, daemon=True)
            t.start()

    @staticmethod
    def _parse_hotkey(hotkey: str) -> set:
        """Parse a hotkey string like 'cmd+shift+t' into a set of pynput key names."""
        from pynput.keyboard import Key

        mapping = {
            "cmd": Key.cmd,
            "command": Key.cmd,
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "alt": Key.alt,
            "option": Key.alt,
            "shift": Key.shift,
            "win": Key.cmd,  # macOS treats win as cmd
        }

        parts = [p.strip().lower() for p in hotkey.split("+")]
        result = set()

        for p in parts:
            if p in mapping:
                result.add(mapping[p])
            elif len(p) == 1:
                # Single character key — use lowercase char
                from pynput.keyboard import KeyCode
                result.add(KeyCode.from_char(p.lower()))
            else:
                # Function key or special
                upper = p.upper()
                if hasattr(Key, upper):
                    result.add(getattr(Key, upper))
                else:
                    result.add(p)

        return result

    @staticmethod
    def _key_name(key) -> str:
        """Get a consistent string name for a key."""
        from pynput.keyboard import Key, KeyCode
        if isinstance(key, KeyCode):
            return key.char or str(key.vk)
        return str(key)
