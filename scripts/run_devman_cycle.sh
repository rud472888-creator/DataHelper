#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/server_jay/Desktop/DataHelper"
PROFILE="devman"
LOCK_FILE="$REPO_ROOT/.devman-cycle.lock"
PROMPT_FILE="$REPO_ROOT/scripts/devman_cycle_prompt.md"
LOG_DIR="$REPO_ROOT/.devman/logs"
CODEX_HOME="/Users/server_jay"
REPO_VENV_BIN="$REPO_ROOT/.venv/bin"
mkdir -p "$LOG_DIR"

if ! /usr/bin/shlock -f "$LOCK_FILE" -p $$; then
  exit 0
fi
trap 'rm -f "$LOCK_FILE"' EXIT

HOME="$CODEX_HOME" PATH="$REPO_VENV_BIN:$PATH" hermes --profile "$PROFILE" chat -q "$(cat "$PROMPT_FILE")" -Q >> "$LOG_DIR/devman-cycle.log" 2>&1
