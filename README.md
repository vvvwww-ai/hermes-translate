# Hermes Translate 🧜‍♀️

macOS 全屏划词即时翻译工具 — **选中即译，零操作**

## 特性

- 🖱️ **选中文本 → 自动弹出译文** — 不需要快捷键，不需要右键菜单
- 🎨 **深色毛玻璃弹窗** — 类终端风格，只显示译文，干净利落
- ⚡ **毫秒级响应** — 剪贴板轮询 + 主线程调度，延迟极低
- 🌐 **DeepL 驱动** — 高质量翻译引擎，多语言支持
- 🚫 **零权限要求** — 不占用辅助功能权限，不需要系统扩展
- 🍔 **菜单栏常驻** — 随时切换目标语言、查看状态

## 使用方式

1. 启动 Hermes Translate（菜单栏出现 🧜‍♀️ 图标）
2. 在任何应用中选中文本，按 **Cmd+C**
3. 译文弹窗自动出现，数秒后自动消失
4. 消失后可以立即选中下一段文本继续翻译

## 安装

### 下载 DMG

从 [Releases](https://github.com/vvsg/hermes-translate/releases) 下载最新的 `.dmg`，拖入 Applications 文件夹即可。

### 从源码运行

```bash
git clone https://github.com/vvsg/hermes-translate.git
cd hermes-translate

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
python -m hermes_translate.app
```

### 构建 .app 包

```bash
# 使用 PyInstaller
pip install pyinstaller
pyinstaller HermesTranslate.spec

# 输出在 dist/Hermes Translate.app
```

## 配置

配置文件路径：`~/.hermes-translate.json`

```json
{
  "api_key": "your-deepl-api-key",
  "target_lang": "ZH"
}
```

首次启动时会提示输入 DeepL API Key。

## 技术栈

- **Python 3** — 核心逻辑
- **PyObjC** — macOS 原生界面（NSPanel、NSVisualEffectView）
- **rumps** — 菜单栏应用框架
- **DeepL API** — 翻译引擎
- **pyperclip** — 剪贴板监听
- **PyInstaller** — 打包为 .app

## 许可证

MIT
