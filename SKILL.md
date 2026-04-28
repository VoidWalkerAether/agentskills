---
name: agentskills
description: Cross-agent skill synchronization tool. Automatically syncs skills across Claude Code, OpenCode, OpenClaw, and Hermes using a unified storage directory with symlinks. Use when the user wants to install, remove, list, update, or sync skills across multiple AI agents.
license: MIT
metadata:
  author: agentskills contributors
  version: 1.0.0
  category: tooling
  language: python
---

# agentskills - 跨智能体技能同步工具

当涉及以下操作时，自动使用此工具同步技能：

## 自动触发场景

**每次新会话开始时**，首先运行：
```bash
agentskills sync
```
这将扫描所有智能体的技能目录，将新技能移动到统一存储 `~/.agent-skills/`，并为所有智能体创建 symlink。

**当用户要求安装/移除/更新/列出技能时**，使用对应的 agentskills 命令：

| 用户意图 | 命令 |
|---------|------|
| 安装新技能 | `agentskills install <url|path> --name <skill-name>` |
| 移除技能 | `agentskills remove <skill-name>` |
| 列出所有技能 | `agentskills list` |
| 查看状态 | `agentskills status` |
| 更新技能 | `agentskills update [skill-name|all]` |
| 同步技能 | `agentskills sync` |
| 完整迁移 | `agentskills migrate` |

## 支持的智能体

| 智能体 | 技能目录 |
|--------|---------|
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenClaw | `~/.openclaw/workspace/skills/` |
| Hermes | `~/.hermes/skills/` |

## 工作原理

1. `~/.agent-skills/` 作为唯一数据源，存放所有技能
2. 各智能体目录通过 symlink 指向统一存储
3. 新技能安装到任一智能体后，运行 `agentskills sync` 即可全局可见
4. 零外部依赖，Python 标准库即可运行

## 安装

如果 `agentskills` 命令不可用，先运行安装脚本：
```bash
curl -fsSL https://raw.githubusercontent.com/VoidWalkerAether/agentskills/main/install.sh | bash
```
或手动安装：
```bash
# 克隆到统一技能目录
git clone https://github.com/VoidWalkerAether/agentskills.git ~/.agent-skills/agentskills-tool
# 创建 PATH symlink
ln -s ~/.agent-skills/agentskills-tool/agentskills.py ~/.local/bin/agentskills
# 安装此 SKILL 到 Claude Code
mkdir -p ~/.claude/skills/agentskills
ln -s ~/.agent-skills/agentskills-tool/SKILL.md ~/.claude/skills/agentskills/SKILL.md
```

## 自动同步配置

安装脚本会自动配置以下 hook。如需手动配置：

### Claude Code
在 `~/.claude/settings.json` 中添加：
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "agentskills sync 2>/dev/null || true" }
        ]
      }
    ]
  }
}
```

### OpenClaw
启用 `boot-md` hook，并在 `~/.openclaw/BOOT.md` 中写入：
```
When starting, first run `agentskills sync 2>/dev/null || true` to sync all skills.
```

### Hermes
与 OpenClaw 相同，在 `~/.hermes/BOOT.md` 中写入：
```
When starting, first run `agentskills sync 2>/dev/null || true` to sync all skills.
```

### OpenCode
OpenCode 暂无原生 hook 支持。建议在 shell profile（`~/.bashrc` / `~/.zshrc`）中添加：
```bash
opencode() {
    agentskills sync 2>/dev/null || true
    command opencode "$@"
}
```

## 使用注意

### 删除技能：两种区别

| 方式 | 影响 |
|------|------|
| 手动删除（如 `rm ~/.claude/skills/xxx`） | 只移除该智能体的 symlink，其他智能体不受影响 |
| `agentskills remove <name>` | 全局删除，所有智能体都不能再使用 |

### 更新技能

- `agentskills update` 只对通过 git 安装的技能有效
- 从本地路径安装的技能不支持自动更新

### 安装方式区别

- `agentskills install` → 直接写入统一存储，所有智能体立即可用
- 手动复制技能到某个智能体目录 → 仅该智能体可见，需运行 `agentskills sync` 才能全局生效
