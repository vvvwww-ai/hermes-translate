# Hermes Translate 🧜‍♀️

> **macOS Copy-to-Translate — Select text, press ⌘C, and see the translation instantly**

A minimalist macOS translation tool. Select text and press **⌘C**; a translation popup appears automatically.
极简 macOS 翻译工具。选中文本后按 **⌘C**，译文弹窗自动弹出。

---

## ✨ Features

- **🖱️ Copy → Translate** — Select text and press **⌘C** to translate. No menus or extra clicks.
  **复制即译** — 选中文本后按 **⌘C** 即可翻译，无需打开菜单或额外点击。
- **🎨 Dark Glassmorphism Popup** — Terminal-style dark frosted glass. Only translation shown, clean and minimal.
  **深色毛玻璃弹窗** — 类终端风格，只显示译文，干净利落。
- **⚡ Fast Response** — Clipboard polling displays translations with low latency.
  **快速响应** — 通过剪贴板轮询，低延迟显示译文。
- **🌐 DeepL Powered** — High-quality translation engine, supports 20+ languages.
  **DeepL 驱动** — 高质量翻译引擎，支持 20+ 语言。
- **🚫 No Accessibility Permissions Required** — No Accessibility permissions or system extensions needed.
  **无需辅助功能权限** — 不需要辅助功能权限或系统扩展。
- **🍔 Menu Bar App** — Switch target language and check status from the menu bar anytime.
  **菜单栏常驻** — 随时切换目标语言、查看状态。

## 📸 Usage

1. Launch **Hermes Translate** (🧜‍♀️ icon appears in the menu bar)
2. Select text in any app and press **⌘C**
3. The translation popup appears automatically and dismisses after a few seconds
4. Copy another selection to translate it

**使用方法：**

1. 启动 **Hermes Translate**（菜单栏出现 🧜‍♀️ 图标）
2. 在任意应用中选中文本并按 **⌘C**
3. 译文弹窗自动出现，数秒后消失
4. 复制另一段文本即可继续翻译

## 📥 Installation

### Download DMG (Recommended)

Download the latest `.dmg` from [Releases](https://github.com/vvvwww-ai/hermes-translate/releases), drag to Applications.
从 [Releases](https://github.com/vvvwww-ai/hermes-translate/releases) 下载最新的 `.dmg`，拖入 Applications 文件夹即可。

### Run from Source

```bash
git clone https://github.com/vvvwww-ai/hermes-translate.git
cd hermes-translate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m hermes_translate.app
```

### Build .app Package

```bash
# Install py2app
pip install py2app setuptools

# Build .app
python setup_py2app.py py2app

# Output in dist/Hermes Translate.app
```

## ⚙️ Configuration

Configuration file: `~/.hermes-translate.json`

```json
{
  "api_key": "your-deepl-api-key",
  "target_lang": "ZH"
}
```

API Key is prompted on first launch. 首次启动时会提示输入 DeepL API Key。

## 🛠️ Tech Stack

| Tech | Purpose |
|------|---------|
| **Python 3** | Core logic |
| **PyObjC** | macOS native UI (NSPanel, NSVisualEffectView) |
| **rumps** | Menu bar app framework |
| **DeepL API** | Translation engine |
| **pyperclip** | Clipboard monitoring |
| **py2app** | Packaging for .app bundle |

## 📄 License

MIT
