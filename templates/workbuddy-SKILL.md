---
name: coding-standard
description: 写代码统一规范的入口技能。凡是涉及写代码、改代码、重构、写 SQL、代码审查、安全审查、运行时排错的任务都必须加载：新增功能、修 bug、加接口、改脚本、优化慢查询、review diff、查漏洞、定位线上问题。规则本体不在本技能内，在 ~/.agent-rules/CODING.md（与 Codex / Claude Code / Cursor / Trae 共用同一份）。
agent_created: true
version: 2.0.0
display_name: "写代码规范（多工具统一）"
---

# 写代码规范

## ⚠️ 规则本体不在本文件

唯一权威：**`~/.agent-rules/CODING.md`**

它同时被分发到 Codex / Claude Code / Cursor / Trae。**本技能不保存规则副本**——否则会出现两套规则打架。
要改规则，改 `CODING.md`，然后跑 `python ~/.agent-rules/sync.py`。

---

## 第一步（强制，不许跳）

用 Read 打开 `~/.agent-rules/CODING.md`，按它的内容执行。

那份文件里有：

- 优先级（P0 用户规则 > P1 项目现状 > P2 语言惯例）
- 动手前 60 秒的读现场四步
- **P0 二十三条硬规则速查**（方法 ≤80 行、叙事性、拆分三问、链式适度、嵌套 ≤2 层、命名后缀、集合返回空、日志异常、常量与注释、不重排别人代码、对象变量用类型名、类名后缀分层、工具先找现成、现代 API 优先、并发按场景、包装类与基本类型、循环与性能、数据载体分包、不建内部类、协议取值用枚举、参数上下文对象、SQL 落 XML、不 Map 套 Map）
- 八条通用铁律
- 禁裸 `List<Map>` / `dict` / `any`
- 验证纪律（各语言最低验证动作 + 汇报三态）
- 汇报格式

## 第二步：按场景读分册

分册都在 `~/.agent-rules/references/`：

| 场景 | 分册 |
|---|---|
| 要细究某条 P0、判断写法是否违规 | `p0-detail.md` |
| Java / Spring Boot / MyBatis-Plus | `java-backend.md` |
| JE 平台数据访问、Controller 写法 | `je-platform.md` |
| 写/改 SQL、跨库转换 | `sql.md`（方言 `sql-dialects.md`） |
| 写/改 Vue 2 前端页面 | `frontend-vue2.md` |
| 新增或改接口 | `api-design.md` |
| 提交代码、写 commit message | `git-convention.md` |
| 链式 / Stream / Optional | `style-chain.md` |
| 要看反面案例、验证命令细节 | `anti-patterns.md` |
| 用户要求 review diff/MR/PR | `review.md` |
| 用户要求安全审查、漏洞扫描 | `security-review.md` |
| Web 代码安全基线 | `security-general.md` → `security/<lang>-<framework>-<stack>-security.md` |
| 用户直接要求调试/定位根因 | `debug.md` |
| 用户完整原始规则（含需求处理偏好） | `user-rules.md` |

**只读该读的那一份，不要一次全读。**

---

## 兜底

如果 `CODING.md` 不存在：

1. 立刻告诉用户"统一规范文件丢失了"
2. 不要凭记忆临时编一套规则
3. 用 `references/user-rules.md` 里那 10 条 P0 作为最低底线先扛着，并提示用户重建

---

## 与其他技能的边界

- 专用报表模板（如 `.rpx`）解析/字段核对 → 对应的报表解析技能，本规范只约束里面的 SQL 写法
- Office 文档/表格生成 → 对应 Office 技能
- 本规范管：**代码怎么写、怎么改、怎么审、怎么验证**
