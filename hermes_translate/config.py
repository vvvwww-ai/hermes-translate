"""
Configuration management for Hermes Translate.
Reads from ~/.hermes-translate.json or environment variables.
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes-translate.json"

DEFAULTS = {
    "deepl_api_key": "",         # Get yours at: https://www.deepl.com/pro-api
    "source_lang": "",           # "" = auto-detect
    "target_lang": "ZH",         # Default: translate to Chinese
    "hotkey": "cmd+shift+t",     # Global hotkey
    "window_width": 520,
    "window_max_height": 600,
    "font_family": "SF Pro Display",
    "font_size_original": 13,
    "font_size_translation": 16,
    "opacity": 0.96,
    "auto_copy": False,          # Auto-copy translation to clipboard
    "show_original": True,       # Show original text in overlay
}


def load_config() -> dict:
    """Load config from disk, merge with defaults."""
    config = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user_config = json.load(f)
            config.update(user_config)
        except (json.JSONDecodeError, IOError):
            pass

    # Env var overrides
    if os.environ.get("DEEPL_API_KEY"):
        config["deepl_api_key"] = os.environ["DEEPL_API_KEY"]
    if os.environ.get("TRANSLATE_TARGET_LANG"):
        config["target_lang"] = os.environ["TRANSLATE_TARGET_LANG"]

    return config


def save_config(config: dict) -> None:
    """Save config to disk."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
