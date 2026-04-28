# agentskills - 跨智能体技能统一管理工具

一个本地 CLI 工具，解决多个 AI 智能体（Claude Code、OpenCode、OpenClaw、Hermes）之间技能重复安装、无法共享的问题。核心方案：`~/.agent-skills/` 作为唯一数据源，通过 symlink 桥接到各智能体的技能目录。

## 开发规则

1. **每次只实现一个功能**，完成后更新 CHANGELOG.md 再进入下一个
2. **测试优先**：每个功能完成后验证其可用性
3. **保持代码可运行**：每次提交后，工具必须能正常执行
4. **提交规范**：每完成一个功能就 `git commit`，message 格式：`feat: [功能名] - 简要说明`
5. **不要 push**：只 commit 到本地，完成时提醒用户手动 push
6. **Python 单文件，零外部依赖**

## 智能体目录映射

| 智能体 | 技能目录 |
|--------|---------|
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenClaw | `~/.openclaw/workspace/skills/` |
| Hermes | `~/.hermes/skills/` |

## 技术实现

### 语言
Python 3（shebang `#!/usr/bin/env python3`），零外部依赖，仅用标准库。

### 文件结构
```
~/.agent-skills/            ← 统一技能存储目录
  .agentskills/             ← 元数据
    config.json             ← 工具配置
    registry.json           ← 技能注册表

agentskills/                ← 本项目代码
  agentskills.py            ← 单文件 CLI 工具
  SKILL.md                  ← 技能描述文件（AI agent 可读）
  install.sh                ← 一键安装脚本
  CHANGELOG.md              ← 变更记录
  CLAUDE.md                 ← 本文件
```

### 安装方式
```bash
# 一键安装
curl -fsSL https://raw.githubusercontent.com/VoidWalkerAether/agentskills/main/install.sh | bash

# 或手动安装
ln -s <项目路径>/agentskills.py ~/.local/bin/agentskills
```

## 设计要点

- **去重策略**：多个智能体有同名技能时，保留修改时间最新的一份到 `~/.agent-skills/`
- **symlink 策略**：对每个智能体目录，创建指向 `~/.agent-skills/<skill>/` 的 symlink
- **已有 symlink 检测**：跳过已经是 symlink 的条目，不重复创建
- **git 技能检测**：检查技能目录是否有 `.git`，决定 update 命令的行为
- **安全**：不删除非 symlink 的目录内容（除非确认是重复技能）
