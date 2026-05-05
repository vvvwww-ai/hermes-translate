"""
Hermes Translate — 全屏划词即时翻译
V2: direct performSelectorOnMainThread dispatch — no timer delay.
"""

import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import Optional

import rumps
import pyperclip
import objc
from Foundation import NSObject

from .config import load_config, save_config, CONFIG_PATH
from .translator import get_translator, LANG_NAMES


class _MainThreadBridge(NSObject):
    """Helper to dispatch calls to main thread via performSelector."""

    def initWithTarget_andSelector_(self, target, selector_name):
        self = objc.super(_MainThreadBridge, self).init()
        self._target = target
        self._selector = selector_name
        return self

    def invoke_(self, _):
        getattr(self._target, self._selector)()


class HermesTranslateApp(rumps.App):
    """Menu bar app — monitors clipboard for new text, auto-translates."""

    def __init__(self):
        super().__init__(name="HermesTranslate", title="🌐", quit_button="退出")
        self.config = load_config()
        self.translator = get_translator(api_key=self.config.get("deepl_api_key", ""))
        self._overlay_active = False
        self._rapid_poll_until = 0
        self._last_change_count = 0
        self._last_translated = ""
        self._last_clipboard = ""
        self._monitor_running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._main_bridge = _MainThreadBridge.alloc().initWithTarget_andSelector_(
            self, '_show_and_loop'
        )

        self._build_menu()
        self._start_clipboard_monitor()

        engine = "MyMemory (免费)" if not self.config.get("deepl_api_key") else "DeepL"
        rumps.notification(
            title="Hermes Translate 已启动",
            subtitle=f"引擎: {engine}",
            message="选中文字 → Cmd+C 复制 → 自动翻译",
        )

    # ─── Menu ────────────────────────────────────────────────────

    def _build_menu(self):
        tgt = self.config.get("target_lang", "ZH")
        self.target_menu = rumps.MenuItem(f"目标语言: {LANG_NAMES.get(tgt, tgt)}")
        for code, name in [
            ("ZH", "中文"), ("EN", "英语"), ("JA", "日语"),
            ("KO", "韩语"), ("FR", "法语"), ("DE", "德语"),
        ]:
            item = rumps.MenuItem(f"  {name} ({code})", callback=self._set_target_lang)
            item.state = 1 if code == tgt else 0
            self.target_menu.add(item)
        self.menu = [
            rumps.MenuItem("⚙️ 设置向导", callback=self._run_setup),
            self.target_menu,
            None,
            rumps.MenuItem("⏸ 暂停 / 继续", callback=self._toggle_monitor),
            rumps.MenuItem("📋 关于", callback=self._about),
        ]

    def _set_target_lang(self, sender):
        code = str(sender.title).split("(")[-1].rstrip(")")
        self.config["target_lang"] = code
        save_config(self.config)
        self.target_menu.title = f"目标语言: {LANG_NAMES.get(code, code)}"
        for item in self.target_menu.values():
            item.state = 1 if str(item.title).split("(")[-1].rstrip(")") == code else 0
        rumps.notification(title="Hermes Translate", subtitle="语言已切换",
                          message=f"→ {LANG_NAMES.get(code, code)}")

    def _toggle_monitor(self, sender):
        if self._monitor_running:
            self._stop_monitor()
            sender.title = "▶ 继续翻译"
            rumps.notification(title="Hermes Translate", subtitle="已暂停", message="")
        else:
            self._start_clipboard_monitor()
            sender.title = "⏸ 暂停"
            rumps.notification(title="Hermes Translate", subtitle="已恢复", message="")

    # ─── Monitor ─────────────────────────────────────────────────
    def _start_clipboard_monitor(self):
        """Start polling clipboard for new text."""
        self._monitor_running = True
        try:
            self._last_clipboard = pyperclip.paste()
        except Exception:
            self._last_clipboard = ""
        # Use NSPasteboard.changeCount for reliable change detection
        from AppKit import NSPasteboard
        self._last_change_count = NSPasteboard.generalPasteboard().changeCount()
        self._monitor_thread = threading.Thread(target=self._clipboard_loop, daemon=True)
        self._monitor_thread.start()

    def _stop_monitor(self):
        self._monitor_running = False

    def _clipboard_loop(self):
        from AppKit import NSPasteboard
        pb = NSPasteboard.generalPasteboard()
        while self._monitor_running:
            cc = pb.changeCount()
            if cc != self._last_change_count and not self._overlay_active:
                self._last_change_count = cc
                try:
                    current = pyperclip.paste()
                except Exception:
                    time.sleep(0.12)
                    continue
                if (current and len(current.strip()) >= 3 and
                    self._looks_like_translatable(current.strip())):
                    text = current.strip()
                    if len(text) > 5000:
                        text = text[:5000] + "..."
                    self._translate_and_show(text)

            if getattr(self, '_rapid_poll_until', 0) > time.time():
                time.sleep(0.03)
            else:
                time.sleep(0.12)

    @staticmethod
    def _looks_like_translatable(text):
        if text.startswith("http://") or text.startswith("https://"):
            return False
        if text.startswith("/") and "/" in text[1:] and len(text.split()) == 1:
            return False
        return sum(1 for c in text if c.isalpha()) >= 2

    # ─── Callbacks ───────────────────────────────────────────────

    def _run_setup(self, _=None):
        import json
        config_path = Path.home() / ".hermes-translate.json"
        if not config_path.exists():
            template = {"deepl_api_key": "", "target_lang": "ZH", "source_lang": ""}
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        subprocess.run(["open", str(config_path)])
        rumps.notification(title="Hermes Translate", subtitle="配置文件已打开",
                          message="保存后下次翻译自动生效")

    def _about(self, _=None):
        engine = "MyMemory (免费)" if not self.config.get("deepl_api_key") else "DeepL"
        rumps.alert(title="Hermes Translate v2.0", message=(
            f"划词即时翻译\n引擎: {engine}\n\n选中文字 → Cmd+C → 自动弹窗！"
        ))

    # ─── Translation (async: loading panel → API → update) ───────

    def _translate_and_show(self, text: str):
        self._overlay_active = True
        self.config = load_config()
        self.translator = get_translator(api_key=self.config.get("deepl_api_key", ""))

        # Dispatch panel creation to main thread NOW
        self._pending_panel = True
        self._main_bridge.performSelectorOnMainThread_withObject_waitUntilDone_(
            'invoke:', None, False
        )

        # API call in background
        try:
            translated, _, _ = self.translator.translate(
                text, source_lang=self.config.get("source_lang", ""),
                target_lang=self.config.get("target_lang", "ZH"),
            )
            self._last_translated = self._last_clipboard
            self._pending_translation = translated
        except Exception as e:
            self._pending_translation = f"翻译失败: {e}"
        self._translation_ready = True

        # Wait for panel dismiss
        while self._overlay_active:
            time.sleep(0.1)
        self._overlay_active = False
        self._translation_ready = False

    def _show_and_loop(self):
        """Called on main thread — show panel, run nested event loop."""
        from .overlay import show_loading, update_translation, is_dismissed
        from AppKit import NSApp, NSDate, NSDefaultRunLoopMode

        if not getattr(self, '_pending_panel', False):
            return
        self._pending_panel = False

        show_loading("…")

        while not is_dismissed():
            NSApp.nextEventMatchingMask_untilDate_inMode_dequeue_(
                0xFFFFFFFF, NSDate.dateWithTimeIntervalSinceNow_(0.001),
                NSDefaultRunLoopMode, True,
            )
            if getattr(self, '_translation_ready', False):
                self._translation_ready = False
                text = getattr(self, '_pending_translation', '')
                if text:
                    update_translation(text)

        self._overlay_active = False
        self._rapid_poll_until = time.time() + 0.8

        # Sync changeCount so current clipboard won't re-trigger
        from AppKit import NSPasteboard
        self._last_change_count = NSPasteboard.generalPasteboard().changeCount()


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    if "--setup" in sys.argv:
        _run_setup_cli()
    elif "--help" in sys.argv or "-h" in sys.argv:
        _print_help()
    else:
        HermesTranslateApp().run()


def _run_setup_cli():
    config = load_config()
    print("\n🔧 Hermes Translate 设置向导\n")
    api_key = input(f"DeepL API Key [{config.get('deepl_api_key', '未设置')}]: ").strip()
    if api_key:
        config["deepl_api_key"] = api_key
    tgt = input(f"目标语言 [{config.get('target_lang', 'ZH')}]: ").strip().upper()
    if tgt:
        config["target_lang"] = tgt
    src = input(f"源语言 [{config.get('source_lang', '自动')}]: ").strip().upper()
    config["source_lang"] = src if src else ""
    save_config(config)
    print(f"\n✅ 配置已保存到 {CONFIG_PATH}")


def _print_help():
    print("""
Hermes Translate — 划词即时翻译 v2.0
  选中文字 → Cmd+C → 自动弹窗！
  菜单栏 🌐 → ⏸ 可暂停
""")
