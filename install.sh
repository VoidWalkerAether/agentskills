#!/usr/bin/env bash
# agentskills - One-line installer
# Usage: curl -fsSL <repo>/install.sh | bash
#
# This script installs agentskills to ~/.agent-skills/agentskills-tool/
# and creates a symlink in ~/.local/bin/.

set -euo pipefail

REPO_URL="${AGENTSAILS_REPO:-https://github.com/VoidWalkerAether/agentskills}"
BRANCH="${AGENTSAILS_BRANCH:-main}"

echo "=== agentskills installer ==="

# 1. Ensure ~/.local/bin exists and is in PATH
mkdir -p "$HOME/.local/bin"
case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

# 2. Install agentskills.py
TOOL_DIR="$HOME/.agent-skills/agentskills-tool"

if [ -d "$TOOL_DIR/.git" ]; then
    echo "[update] Updating existing installation..."
    git -C "$TOOL_DIR" pull --ff-only
else
    echo "[install] Cloning agentskills to $TOOL_DIR..."
    mkdir -p "$HOME/.agent-skills"
    git clone --depth 1 "$REPO_URL" "$TOOL_DIR"
fi

# 3. Create PATH symlink
LINK="$HOME/.local/bin/agentskills"
if [ -L "$LINK" ]; then
    rm "$LINK"
fi
ln -s "$TOOL_DIR/agentskills.py" "$LINK"
echo "[ok] agentskills installed to $LINK"

# 4. Install SKILL.md to Claude Code skills directory
SKILL_DIR="$HOME/.claude/skills/agentskills"
if [ -f "$TOOL_DIR/SKILL.md" ]; then
    mkdir -p "$SKILL_DIR"
    rm -f "$SKILL_DIR/SKILL.md"
    ln -s "$TOOL_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
    echo "[ok] SKILL.md installed to $SKILL_DIR"
fi

# 5. Configure auto-sync for Claude Code (SessionStart hook)
SETTINGS="$HOME/.claude/settings.json"
if command -v python3 &>/dev/null; then
    python3 -c "
import json, sys
settings_file = '$SETTINGS'
try:
    with open(settings_file) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

hook = {
    'hooks': [
        {'type': 'command', 'command': 'agentskills sync 2>/dev/null || true'}
    ]
}

hooks = settings.setdefault('hooks', {})
existing = hooks.get('SessionStart', [])
# Check if already configured
if not any('agentskills' in str(h) for h in existing):
    existing.append(hook)
    hooks['SessionStart'] = existing
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    print('[ok] Claude Code SessionStart hook configured')
else:
    print('[skip] Claude Code SessionStart hook already configured')
"
fi

# 6. Configure auto-sync for OpenClaw / Hermes (BOOT.md)
BOOT_CONTENT="# Auto-sync skills on startup
# Managed by agentskills installer - do not edit manually
When the session starts, first run \`agentskills sync 2>/dev/null || true\` to synchronize all skills across agents, then proceed normally."

for agent_dir in "$HOME/.openclaw" "$HOME/.hermes"; do
    if [ -d "$agent_dir" ]; then
        boot_file="$agent_dir/BOOT.md"
        if [ ! -f "$boot_file" ] || ! grep -q "agentskills" "$boot_file" 2>/dev/null; then
            echo "$BOOT_CONTENT" > "$boot_file"
            echo "[ok] BOOT.md configured in $agent_dir"
        fi
    fi
done

# 7. Final sync
echo ""
echo "[sync] Running initial sync..."
agentskills sync

echo ""
echo "=== Installation complete ==="
echo "  Run 'agentskills --help' to get started"
echo "  Run 'agentskills list' to see all skills"
