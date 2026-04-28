# agentskills

Cross-agent skill synchronization tool. Install a skill once, use it everywhere.

[中文版本](#简体中文) · [English](#agentskills)

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/VoidWalkerAether/agentskills/master/install.sh | bash
```

## Usage

```bash
agentskills sync            # Sync skills across all agents
agentskills list            # List all installed skills
agentskills install <url> --name <name>  # Install a new skill
agentskills remove <name>   # Remove a skill
agentskills status          # Check for issues
agentskills update [name|all]  # Update skills from git
```

## How It Works

```
~/.agent-skills/          ← Single source of truth for all skills
  ├── skill-a/
  ├── skill-b/
  └── ...

Claude Code: ~/.claude/skills/skill-a → symlink → ~/.agent-skills/skill-a/
OpenCode:    ~/.config/opencode/skills/skill-a → symlink → ~/.agent-skills/skill-a/
OpenClaw:    ~/.openclaw/workspace/skills/skill-a → symlink → ~/.agent-skills/skill-a/
Hermes:      ~/.hermes/skills/skill-a → symlink → ~/.agent-skills/skill-a/
```

Each agent's skill directory symlinks to the same location. Change once, update everywhere.

## Supported Agents

| Agent | Skill Directory |
|-------|----------------|
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenClaw | `~/.openclaw/workspace/skills/` |
| Hermes | `~/.hermes/skills/` |

## Features

- **Zero dependencies**: Pure Python standard library, no pip install needed
- **Deduplication**: Automatically keeps the latest version when duplicate skills exist
- **Safe**: Never deletes non-symlink files to prevent accidental data loss
- **Auto-sync**: Automatically detects and syncs new skills on session start

## Manual Install

```bash
# Clone to unified skills directory
git clone https://github.com/VoidWalkerAether/agentskills.git ~/.agent-skills/agentskills-tool

# Create PATH symlink
ln -s ~/.agent-skills/agentskills-tool/agentskills.py ~/.local/bin/agentskills

# Install SKILL.md to Claude Code
mkdir -p ~/.claude/skills/agentskills
ln -s ~/.agent-skills/agentskills-tool/SKILL.md ~/.claude/skills/agentskills/SKILL.md
```

---

## 简体中文

跨智能体技能同步工具。安装一次，所有智能体共享。

### 一行安装

```bash
curl -fsSL https://raw.githubusercontent.com/VoidWalkerAether/agentskills/master/install.sh | bash
```

安装后自动完成：
- 将 `agentskills` 命令添加到 PATH
- 将 SKILL.md 安装到 Claude Code 技能目录
- 配置各智能体的自动同步 hook
- 执行首次技能同步

### 使用方法

```bash
agentskills sync            # 同步所有智能体的技能
agentskills list            # 列出已安装的技能
agentskills install <url> --name <name>  # 安装新技能
agentskills remove <name>   # 删除技能
agentskills status          # 检查问题
agentskills update [name|all]  # 从 git 更新技能
```

### 工作原理

```
~/.agent-skills/          ← 唯一数据源，存放所有技能
  ├── skill-a/
  ├── skill-b/
  └── ...

Claude Code: ~/.claude/skills/skill-a → symlink → ~/.agent-skills/skill-a/
OpenCode:    ~/.config/opencode/skills/skill-a → symlink → ~/.agent-skills/skill-a/
OpenClaw:    ~/.openclaw/workspace/skills/skill-a → symlink → ~/.agent-skills/skill-a/
Hermes:      ~/.hermes/skills/skill-a → symlink → ~/.agent-skills/skill-a/
```

每个智能体通过 symlink 指向同一份技能文件，修改一处，全局生效。

### 支持的智能体

| 智能体 | 技能目录 |
|--------|---------|
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenClaw | `~/.openclaw/workspace/skills/` |
| Hermes | `~/.hermes/skills/` |

### 特性

- **零外部依赖**：纯 Python 标准库，无需 pip install
- **去重**：同名技能自动保留最新版本
- **安全**：不删除非 symlink 的文件，避免误操作
- **自动同步**：新会话启动时自动检测并同步新技能

### 手动安装

```bash
# 克隆到统一技能目录
git clone https://github.com/VoidWalkerAether/agentskills.git ~/.agent-skills/agentskills-tool

# 创建 PATH symlink
ln -s ~/.agent-skills/agentskills-tool/agentskills.py ~/.local/bin/agentskills

# 安装 SKILL.md 到 Claude Code
mkdir -p ~/.claude/skills/agentskills
ln -s ~/.agent-skills/agentskills-tool/SKILL.md ~/.claude/skills/agentskills/SKILL.md
```

## License

MIT
