# 统一编码规范 · 多工具分发

一份规则，五个工具共用。改一次，全部生效。

## 架构

```
~/.agent-rules/
├── CODING.md            ★ 唯一权威，改这里
├── sync.py              分发脚本
├── README.md            本文件
├── templates/           整文件复制的模板（workbuddy-SKILL.md）
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
| **WorkBuddy** | `~/.workbuddy/skills/coding-standard/SKILL.md` | 整文件复制（模板 `templates/workbuddy-SKILL.md`） | ✅ 确认 |
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

---

## 接入第二台电脑

仓库地址：**https://github.com/xiangbiaoqiao/agent-rules**（公开库，clone 无需认证）

前提：装好 **Python 3** 和 **Git**（`python --version` / `git --version` 能出版本号）。

### 方式一：git（推荐，长期同步）

#### 1.1 认证（公开库可跳过）

> 当前是公开库，**不需要任何认证**，直接跳到 1.2。
> 若以后改为私有库，按下面任选一种配置即可。

**A. gh CLI（推荐，配一次长期有效）**

```bash
# 安装
winget install --id GitHub.cli      # Windows
brew install gh                     # macOS

# 登录：选 HTTPS，浏览器点一下授权
gh auth login
```

`gh auth login` 会顺手配好 git 的凭证助手，之后 `clone` / `pull` / `push` 都不再问账号密码，
凭证存在系统凭据管理器里，重启也有效。

**B. PAT（不想装 gh 时）**

GitHub → Settings → Developer settings → Personal access tokens 生成一个带 `repo` 权限的令牌：

```bash
git clone https://<你的token>@github.com/xiangbiaoqiao/agent-rules.git ~/.agent-rules
```

> 缺点：token 会明文留在 `.git/config`，且有过期时间；用完别把仓库目录整体分享出去。

#### 1.2 克隆并分发

```bash
# 克隆到家目录（路径必须是 ~/.agent-rules，sync.py 认这个位置）
git clone https://github.com/xiangbiaoqiao/agent-rules.git ~/.agent-rules

# 分发到各工具
python ~/.agent-rules/sync.py

# 验证
python ~/.agent-rules/sync.py --check
```

之后两台机器保持同步：

```bash
cd ~/.agent-rules
git pull          # 干活前先拉
# 改了 CODING.md 之后
git add -A && git commit -m "更新规则：xxx" && git push
```

> 改了规则一定要 `commit + push`，否则另一台机器永远是旧的。
> 建议养成「改完 CODING.md → sync.py → commit push」一条龙。

### 方式二：压缩包（没网 / 不方便建仓库时）

1. 在**有规范的那台**上打包（`.git` 可带可不带）：
   ```bash
   cd ~ && tar -czf agent-rules.tar.gz .agent-rules
   ```
2. 拷到另一台（U 盘 / 微信 / 内网共享都行），解压到 `C:\Users\<你的用户名>\`：
   ```bash
   cd ~ && tar -xzf agent-rules.tar.gz
   ```
3. 跑 `python ~/.agent-rules/sync.py`

> 这种方式下次改规则还得再拷一遍，只适合应急。

### 跨机器注意事项

- **路径全部用 `Path.home()` 动态解析**，两台机器用户名不同也没问题（`sync.py` 和 SKILL.md 里原先写死的绝对路径已改成动态 / `~/`）
- 目标工具（Codex / Cursor / Claude Code ...）**这台机器上没装的话，sync 会自动建目录**，不影响使用；装了哪个就用哪个
- **不要把 `~/.agent-rules` 放进 OneDrive / 坚果云同步盘**：`.git` 在同步盘上冲突起来很难修
- 旧机器的入口文件不用删，各自独立生成

---

## 修改记录

| 日期 | 内容 |
|---|---|
| 2026-11-09 | 加 git 版本管理（`.gitignore` / `.gitattributes`，统一 LF）；修掉 `sync.py` 与 SKILL.md 里写死的 `C:\Users\27188` 路径；WorkBuddy 技能纳入 `kind=copy` 分发；`CANON` 改为按脚本位置定位；补「接入第二台电脑」章节；**仓库定为公开库**（曾切私有实测认证流程，README 保留 gh / PAT 两种方式备查） |

