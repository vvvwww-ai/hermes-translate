#!/bin/bash
# ─────────────────────────────────────────────────────
#  Hermes Translate 启动脚本
#  用法: ./run.sh [--setup]
# ─────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"

# Check venv
if [ ! -f "$VENV_PYTHON" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv "$SCRIPT_DIR/venv"
    "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
fi

# Run
cd "$SCRIPT_DIR"
exec "$VENV_PYTHON" -m hermes_translate "$@"
