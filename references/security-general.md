# 安全编码基线

融合自 Codex `security-best-practices`。用于**写新代码时默认安全**、或**被动发现**严重问题。
用户要正式安全报告 → 走 `security-review.md`。

---

## 1. 工作流

1. **识别技术栈**：列出范围内全部语言 + 框架（前后端都要看，别只看后端）。
2. **查 references/security/** 目录，文件名格式 `<language>-<framework>-<stack>-security.md`：
   - 有匹配框架的 → 读该文件
   - 再读 `<language>-general-<stack>-security.md`（框架无关部分）
   - 前后端都在范围 → **两边都要读**
   - 前端框架未指定但要做 Web 应用 → 读 `javascript-general-web-frontend-security.md`
3. 无匹配文档 → 用已知的该语言安全最佳实践，并在产出报告时说明"没有具体指导文档"。

## 2. 三种模式

| 模式 | 场景 | 做法 |
|---|---|---|
| **默认（主）** | 写新代码 | 直接按最佳实践写，不提额外要求 |
| **被动** | 在项目里干活时顺带发现 | 只提示**影响最大**的严重问题 + 安全默认值 |
| **报告** | 用户明确要求 | 出分级报告，写完给出位置并摘要 |

## 3. 可覆盖

项目文档/prompt 里明确要求绕过某条最佳实践时，**服从项目**。可以提示一句，但不要跟用户争。
建议把绕过理由写进项目文档，方便后来人。

## 4. 通用安全建议

### 公开资源 ID 别用自增
对外暴露的资源 ID 用 UUID4 或随机十六进制串，不用小自增。否则用户能推算总量、猜测 ID。

### TLS 的判断要谨慎
- **不要**因为开发环境没开 TLS 就报安全问题。
- `secure` cookie 只在应用真的跑在 TLS 上才设，否则会直接把应用搞挂。给个 env 开关控制。
- **不要**建议加 HSTS——理解不充分时上 HSTS 会造成长时间无法逆转的故障和用户锁死。

## 5. 修复纪律

- 一次只修一条发现。
- 修复注释里点明依据的是哪条最佳实践，以及不这么做会有什么危险（一句话即可）。
- **先评估是否会破坏现有功能。** 不安全的代码往往长期存活正是因为有别的依赖——直接改可能引发回归。写之前想清楚，改之后跑一遍项目原有的测试流程。
- 遵循用户既有的提交规范；提交信息说明这是安全对齐；不要把多条无关发现塞进一个 commit。
- 二次影响（上下游依赖旧行为）要在动手前告知用户。

## 6. references/security/ 索引

| 文件 | 覆盖 |
|---|---|
| `golang-general-backend-security.md` | Go 后端通用 |
| `python-django-web-server-security.md` | Django |
| `python-fastapi-web-server-security.md` | FastAPI |
| `python-flask-web-server-security.md` | Flask |
| `javascript-express-web-server-security.md` | Express |
| `javascript-typescript-nextjs-web-server-security.md` | Next.js |
| `javascript-general-web-frontend-security.md` | 通用前端（框架无关） |
| `javascript-typescript-react-web-frontend-security.md` | React |
| `javascript-typescript-vue-web-frontend-security.md` | Vue |
| `javascript-jquery-web-frontend-security.md` | jQuery |

**按需读取，不要一次全读。** 只读匹配当前栈的那几份。

## 7. 报告格式（用户要求时）

文件写到 `security_best_practices_report.md`（或用户指定位置），结构：

1. 执行摘要（短）
2. 按严重度分节：CRITICAL / HIGH / MEDIUM / LOW
3. 每条发现带数字编号，便于引用
4. CRITICAL 级必须有一句影响说明
5. 引用代码时**必须带行号**

写完在对话里简要摘要，并告知文件位置。之后询问是否开始修复（逐条修）。
