# agentskills

跨智能体技能同步工具。统一管理 Claude Code、OpenCode、OpenClaw、Hermes 等 AI 智能体的技能，让安装一次的技能在所有智能体间自动可见。

## 一行安装

```bash
curl -fsSL https://raw.githubusercontent.com/VoidWalkerAether/agentskills/main/install.sh | bash
```

安装后自动：
- 配置 `agentskills` 命令到 PATH
- 将 SKILL.md 安装到 Claude Code 技能目录
- 配置各智能体的自动同步 hook
- 执行首次技能同步

## 使用方法

```bash
# 同步所有智能体的技能
agentskills sync

# 查看已安装的技能
agentskills list

# 安装新技能
agentskills install <url|path> --name <skill-name>

# 移除技能
agentskills remove <skill-name>

# 查看状态
agentskills status

# 更新技能
agentskills update [skill-name|all]
```

## 工作原理

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

## 手动安装

```bash
# 克隆到统一技能目录
git clone https://github.com/VoidWalkerAether/agentskills.git ~/.agent-skills/agentskills-tool

# 创建 PATH symlink
ln -s ~/.agent-skills/agentskills-tool/agentskills.py ~/.local/bin/agentskills

# 安装 SKILL.md 到 Claude Code
mkdir -p ~/.claude/skills/agentskills
ln -s ~/.agent-skills/agentskills-tool/SKILL.md ~/.claude/skills/agentskills/SKILL.md
```

## 支持的智能体

| 智能体 | 技能目录 |
|--------|---------|
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenClaw | `~/.openclaw/workspace/skills/` |
| Hermes | `~/.hermes/skills/` |

## 特性

- **零外部依赖**：纯 Python 标准库，无需 pip install
- **去重**：同名技能自动保留最新版本
- **安全**：不删除非 symlink 的文件，避免误操作
- **自动同步**：新会话启动时自动检测并同步新技能

## License

MIT
