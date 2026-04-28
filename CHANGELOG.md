# Changelog

## 0.1.0 (2026-04-28)

### 新增
- `agentskills init` — 初始化统一技能存储目录 `~/.agent-skills/`
- `agentskills sync` — 扫描各智能体技能目录，去重、移动到统一存储、创建 symlink
- `agentskills list` — 列出所有技能及在各智能体中的状态（symlink/local/missing）
- `agentskills install` — 从 git URL 或本地路径安装新技能到统一存储
- `agentskills remove` — 从所有智能体删除指定技能
- `agentskills status` — 检查 broken symlink 和未收敛技能
- `agentskills update` — git pull 更新指定技能或全部
- `agentskills migrate` — 一键迁移向导

### 首次迁移
- 从 Claude Code / OpenCode / OpenClaw / Hermes 迁移了 54 个技能到统一存储
- 去重 15 个重复技能
- 创建 214 个 symlink 跨 4 个智能体
