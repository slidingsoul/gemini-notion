#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
exec uv run --project "$SCRIPT_DIR" python "$SCRIPT_DIR/gemini_to_notion.py" "$@"