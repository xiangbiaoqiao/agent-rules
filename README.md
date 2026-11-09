# 统一编码规范 · 多工具分发

一份规则，五个工具共用。改一次，全部生效。

## 架构

```
~/.agent-rules/
├── CODING.md            ★ 唯一权威，改这里
├── sync.py              分发脚本
├── README.md            本文件
├── references/          深主题分册（按需读）
│   ├── java-backend.md
│   ├── sql.md / sql-dialects.md
│   ├── style-chain.md
│   ├── anti-patterns.md
│   ├── review.md
│   ├── security-review.md / security-general.md / security/*.md
│   ├── debug.md
│   └── user-rules.md
└── scripts/debug-server.py
```

分发结果（托管区块，可反复执行，不会覆盖文件里你自己的其它内容）：

| 工具 | 入口文件 | 方式 | 状态 |
|---|---|---|---|
| **Codex** | `~/.codex/AGENTS.md` | 全文内嵌 | ✅ 确认 |
| **Claude Code** | `~/.claude/CLAUDE.md` | 全文内嵌（全局记忆） | ✅ 确认 |
| **Cursor** | `~/.cursor/rules/coding-standard.mdc` | 全文内嵌 + `alwaysApply: true` | ✅ 确认 |
| **Trae CN** | `~/.trae-cn/memory/user_profile.md` | 追加指针，原文保留 | ✅ 确认（UI 规则框另见下） |
| **WorkBuddy** | `~/.workbuddy/skills/coding-standard/SKILL.md` | 技能路由到 CODING.md | ✅ 确认 |
| **CodeBuddy CN** | `~/.codebuddy/skills/coding-standard/SKILL.md` | 技能路由（同 WorkBuddy 生态） | ✅ 结构确认 |
| **OpenCode** | `~/.config/opencode/AGENTS.md` | 全文内嵌 | ✅ 已确认 CLI 读 `AGENTS.md` |
| **ZCode** | `~/.zcode/AGENTS.md` | 全文内嵌 | ⚠️ 未验证 |
| **DeepSeek Harness** | `~/.dsh/AGENTS.md` | 全文内嵌 | ⚠️ 未验证 |
| **CC Switch** | — | 不需要 | 它是 Claude Code 的供应商切换器，不是 agent 本体；CLAUDE.md 照样生效 |

> 标 ⚠️ 的两个：文件已放好，但没核实该工具是否读这个路径。如果它实际支持项目级 `AGENTS.md`，
> 那个方式一定生效——把 `CODING.md` 复制到你的项目根目录改名 `AGENTS.md` 即可。

## 改规则的三步

```bash
# 1. 编辑权威文件
notepad ~/.agent-rules/CODING.md

# 2. 分发
python ~/.agent-rules/sync.py

# 3. 确认
python ~/.agent-rules/sync.py --check
```

`--check` 会比对每份文件的 hash 标记，过期返回退出码 1。随时可以跑一下看有没有漂移。

想加新工具：在 `sync.py` 的 `TARGETS` 里加一条，`kind` 选 `block`（全文）或 `pointer`（只放指针）。

## 生效条件

| 工具 | 何时生效 |
|---|---|
| Codex | 新会话 |
| Claude Code | 新会话 |
| Cursor | 新会话 / 重载窗口 |
| CodeBuddy CN | 新会话（技能需刷新注册表） |
| OpenCode | 新会话 |
| Trae CN | 新会话；若 UI 里有独立的「规则」输入框，建议把 CODING.md 粘一次（存 SQLite，脚本写不了） |
| WorkBuddy | 需要重开会话让技能注册表刷新 |
| ZCode / DeepSeek Harness | 待验证是否读取；若不生效改用项目级 AGENTS.md |

## 托管区块说明

每份被写入的文件里都有：

```
<!-- agent-rules:begin hash=xxxxxxxxxxxx | 自动生成，勿手改 -->
...规则正文...
<!-- agent-rules:end -->
```

- 脚本只动这两行标记之间的内容
- 标记之外你可以随便写自己的东西，重跑不会丢
- 想临时禁掉某个工具：把整个区块删掉即可，下次 sync 会重新加回
- 想永久禁掉：从 `sync.py` 的 `TARGETS` 里移除那条

## 规则优先级

```
P0  CODING.md（用户显式设定，跨项目跨语言）
P1  项目现有代码风格
P2  语言/框架通行惯例
```

P0 只约束**新写的代码**，老代码不返工（P0 第 10 条就是这么定的）。
