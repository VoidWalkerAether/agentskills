# agentskills - 跨智能体技能统一管理工具

## 项目概述

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

## 功能路线图（按优先级排序）

### 阶段 1：核心功能
- [ ] 1.1 **CLI 框架** — argparse 入口，`~/.agent-skills/` 目录创建
- [ ] 1.2 **agentskills sync** — 扫描各智能体目录，去重、移动、创建 symlink
- [ ] 1.3 **agentskills list** — 列出所有技能及在各智能体中的状态

### 阶段 2：生命周期管理
- [ ] 2.1 **agentskills install \<url|path\>** — 从 URL 克隆或本地路径安装新技能
- [ ] 2.2 **agentskills remove \<skill\>** — 删除技能及清理所有 symlink
- [ ] 2.3 **agentskills status** — 状态检查（broken symlink、未收敛技能等）

### 阶段 3：维护功能
- [ ] 3.1 **agentskills update \<skill|all\>** — git pull 更新技能
- [ ] 3.2 **agentskills migrate** — 一键迁移现有所有技能到统一架构

## 技术实现

### 语言
Python 3（shebang `#!/usr/bin/env python3`），零外部依赖，仅用标准库。

### 文件结构
```
~/.agent-skills/            ← 统一技能存储目录
  .agentskills/             ← 元数据
    config.json             ← 工具配置
    registry.json           ← 技能注册表（名称、来源、安装时间、git repo）

agentskills/                ← 本项目代码
  agentskills.py            ← 单文件 CLI 工具（安装到 PATH）
  CHANGELOG.md              ← 变更记录
  CLAUDE.md                 ← 本文件
```

### 安装方式
工具完成后，通过 `ln -s <项目路径>/agentskills/agentskills.py ~/.local/bin/agentskills` 或复制脚本到 PATH。

## 设计要点

- **去重策略**：多个智能体有同名技能时，保留修改时间最新的一份到 `~/.agent-skills/`，其余删除
- **symlink 策略**：对每个智能体目录，创建指向 `~/.agent-skills/<skill>/` 的 symlink
- **已有 symlink 检测**：跳过已经是 symlink 的条目，不重复创建
- **git 技能检测**：检查技能目录是否有 `.git`，决定 update 命令的行为
- **安全**：不删除非 symlink 的目录内容（除非确认是重复技能）
