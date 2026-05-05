"""
Translation clients: DeepL (preferred) + MyMemory (free fallback).

DeepL:    https://api-free.deepl.com/v2/translate  (needs API key, 500K chars/mo)
MyMemory: https://api.mymemory.translated.net/get   (no key, ~1000 words/day)
"""

import requests
import urllib.parse
from typing import Optional, Tuple


# Language name mapping
LANG_NAMES = {
    "ZH": "中文",  "EN": "英语",  "JA": "日语",  "KO": "韩语",
    "FR": "法语",  "DE": "德语",  "ES": "西班牙语",
    "PT": "葡萄牙语", "IT": "意大利语", "NL": "荷兰语",
    "PL": "波兰语", "RU": "俄语",   "BG": "保加利亚语",
    "CS": "捷克语", "DA": "丹麦语", "EL": "希腊语",
    "ET": "爱沙尼亚语", "FI": "芬兰语", "HU": "匈牙利语",
    "LT": "立陶宛语", "LV": "拉脱维亚语", "RO": "罗马尼亚语",
    "SK": "斯洛伐克语", "SL": "斯洛文尼亚语", "SV": "瑞典语",
}

# MyMemory language map (DeepL codes → MyMemory codes are mostly the same)
# MyMemory uses lowercase ISO 639-1
MYMEMORY_LANG = {
    "ZH": "zh-CN",
    "EN": "en-GB",
    "JA": "ja",
    "KO": "ko",
    "FR": "fr",
    "DE": "de",
    "ES": "es",
    "PT": "pt",
    "IT": "it",
    "NL": "nl",
    "PL": "pl",
    "RU": "ru",
}


class MyMemoryTranslator:
    """Free translation via MyMemory — no API key needed."""

    API_URL = "https://api.mymemory.translated.net/get"

    def __init__(self):
        self.api_key = ""  # Not needed, kept for interface compatibility

    def translate(
        self,
        text: str,
        source_lang: str = "",
        target_lang: str = "ZH",
    ) -> Tuple[str, str, str]:
        """
        Translate via MyMemory (free, no key).
        """
        # Build langpair: autodetect|TARGET or SOURCE|TARGET
        src = source_lang if source_lang else "autodetect"
        tgt = MYMEMORY_LANG.get(target_lang.upper(), target_lang.lower())
        langpair = f"{src}|{tgt}"

        params = {
            "q": text,
            "langpair": langpair,
        }

        resp = requests.get(
            self.API_URL,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("responseStatus") != 200:
            raise requests.RequestException(
                f"MyMemory error: {data.get('responseDetails', 'unknown')}"
            )

        translated = data["responseData"]["translatedText"]

        # Try to guess source language from match data
        detected = source_lang or "??"
        matches = data.get("matches", [])
        if matches and not source_lang:
            match_src = matches[0].get("source", "")
            if match_src:
                # Extract language code (e.g., "en-GB" → "EN")
                detected = match_src.split("-")[0].upper()

        return translated, detected, target_lang.upper()

    def lang_name(self, code: str) -> str:
        return LANG_NAMES.get(code.upper(), code)


class DeepLTranslator:
    """DeepL API client for text translation (needs API key)."""

    FREE_API = "https://api-free.deepl.com/v2/translate"
    PRO_API = "https://api.deepl.com/v2/translate"

    def __init__(self, api_key: str, use_free_api: bool = True):
        self.api_key = api_key
        self.base_url = self.FREE_API if use_free_api else self.PRO_API

    def translate(
        self,
        text: str,
        source_lang: str = "",
        target_lang: str = "ZH",
    ) -> Tuple[str, str, str]:
        if not self.api_key:
            raise ValueError(
                "DeepL API Key 未设置。\n"
                "请去 https://www.deepl.com/pro-api 注册免费账号获取 Key，\n"
                "然后设置环境变量: export DEEPL_API_KEY='your-key'\n"
                "或写入配置文件: ~/.hermes-translate.json"
            )

        params = {
            "text": text,
            "target_lang": target_lang.upper(),
        }
        if source_lang:
            params["source_lang"] = source_lang.upper()

        headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(
            self.base_url,
            json=params,
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()

        data = resp.json()
        translation = data["translations"][0]
        detected = translation.get("detected_source_language", source_lang or "??")

        return translation["text"], detected, target_lang.upper()

    def lang_name(self, code: str) -> str:
        return LANG_NAMES.get(code.upper(), code)


def get_translator(api_key: str = ""):
    """
    Get the best available translator.
    Returns DeepLTranslator if API key is valid, otherwise MyMemoryTranslator.
    """
    if api_key and _is_valid_deepl_key(api_key):
        return DeepLTranslator(api_key=api_key, use_free_api=True)
    return MyMemoryTranslator()


def _is_valid_deepl_key(key: str) -> bool:
    """Check if a string looks like a valid DeepL API key (UUID format)."""
    key = key.strip()
    # DeepL free keys: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx
    # DeepL pro keys:  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    # Skip Chinese/placeholder text
    if any('\u4e00' <= c <= '\u9fff' for c in key):
        return False
    # Must contain hyphens (UUID format)
    if '-' not in key:
        return False
    # Reasonable length
    if len(key) < 20:
        return False
    return True
