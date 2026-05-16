# Hermes Translate 🧜‍♀️

> **macOS Full-Screen Word Selection Translator — Select & Translate Instantly, Zero Clicks**

A minimalist macOS translation tool. Select any text → press **Cmd+C** → translation popup appears automatically.
极简 macOS 翻译工具。选中文本 → 按 ⌘C → 译文弹窗自动弹出。

---

## ✨ Features

- **🖱️ Select → Auto Translate** — No shortcuts, no right-click menus. Just select and copy.
  **选中即译** — 不需要快捷键，不需要右键菜单。选中即翻译。
- **🎨 Dark Glassmorphism Popup** — Terminal-style dark frosted glass. Only translation shown, clean and minimal.
  **深色毛玻璃弹窗** — 类终端风格，只显示译文，干净利落。
- **⚡ Millisecond Response** — Clipboard polling + main-thread scheduling, ultra-low latency.
  **毫秒级响应** — 剪贴板轮询 + 主线程调度，延迟极低。
- **🌐 DeepL Powered** — High-quality translation engine, supports 20+ languages.
  **DeepL 驱动** — 高质量翻译引擎，支持 20+ 语言。
- **🚫 Zero Permissions Required** — No Accessibility permissions, no system extensions.
  **零权限要求** — 不占用辅助功能权限，不需要系统扩展。
- **🍔 Menu Bar App** — Switch target language, check status from the menu bar anytime.
  **菜单栏常驻** — 随时切换目标语言、查看状态。

## 📸 Usage

1. Launch **Hermes Translate** (🧜‍♀️ icon appears in menu bar)
2. Select any text in any app, press **Cmd+C**
3. Translation popup appears instantly, auto-dismisses after a few seconds
4. Select next text to translate again

**使用方法：**

1. 启动 **Hermes Translate**（菜单栏出现 🧜‍♀️ 图标）
2. 在任何应用中选中文本，按 **Cmd+C**
3. 译文弹窗自动出现，数秒后自动消失
4. 消失后可以立即选中下一段文本继续翻译

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
