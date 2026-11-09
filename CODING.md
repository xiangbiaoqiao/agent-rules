# 统一编码规范（所有 Agent 工具共用）

> **本文件是唯一权威。** 改这里 → `python ~/.agent-rules/sync.py` → 分发到各工具。
> 详细内容在 `~/.agent-rules/references/`，**按需读取，不要一次全读**（见第 8 节索引）。
> 本文件保持精简，是为了让 Agent 真的能读进去——细则一律下沉到分册。

---

## 0. 优先级

```
P0  本文件（用户显式设定，跨项目跨语言）
P1  项目现有代码风格与实际约定
P2  语言/框架通行惯例
```

冲突时 P0 → P1 → P2。**P0 只约束新写的代码，老代码不返工。**

---

## 1. 动手前的 60 秒（不许跳）

1. **判型**：语言、框架、项目类型。
2. **读现场**：被改文件**全文** + 同目录 2–3 个同类文件。看包结构、命名习惯、返回包装类、异常处理、日志写法、注入方式、有无可复用工具。
3. **查依赖**：判断「项目用不用某个库」看 **依赖声明（pom / package.json）+ 全仓使用数**，不能只看当前模块。**新模块零使用 ≠ 项目约定**。
4. **只读该读的分册**（第 8 节）。
5. **先报方案**：一句话说清「改哪几个文件、为什么、影响面」。**超过 3 个文件必须先说。**
6. 动手。
7. **验证**：编译 / 测试 / 实跑。**没跑过不许说完成。**
8. **汇报**：区分「已验证」和「未验证」。

---

## 2. P0 硬规则（23 条速查）

> 每条只有一句判据。**不确定怎么写、或想知道为什么时，读 `references/p0-detail.md`**（完整解释 + 正反例）。

**写法**

1. **方法 ≤ 80 行**，单一职责（校验 / 主逻辑 / 清理三段分层）。
2. **主方法叙事性**：3~7 步调用或 ≤40 行。不是越短越好——拆成 5 个 3 行函数更难读。抽象层次要一致：把每行换成一句话，能连成一段通顺的话。
3. **拆分三问**：会复用吗？>20 行或含复杂嵌套吗？函数名能自解释吗？**全否 → 内联**，禁止纯传话筒函数。
4. **链式适度**：Stream / Builder / Promise 该用；单条件 `if` 不硬塞进链；禁止为链式牺牲可调试性。
5. **嵌套 ≤ 2 层**，超了用卫语句提前 return，不许一直往右缩进。
6. **命名**：集合变量带 `List` / `Map` 后缀；禁 `a`/`b`/`c`/`obj`/`item`/`result`。⚠️ 全局替换防子串：`rows`→`rowList` 会把 `throws` 改坏，替换后必须编译。
7. **集合返回空，不返回 null**（`CollUtil.emptyIfNull`）。
8. **日志与异常**：`{}` 占位符不拼字符串；`catch` 必须带上下文日志，**禁吞异常**；有全局异常处理器时 Controller/Service **不包兜底 try-catch**；对外中文提示，堆栈进日志。
9. **常量与注释**：魔法值常量化；公共方法写 Javadoc；函数体内注释只写「为什么」。常量按职责归位（多类共用→独立常量类，单类→`private`），声明处不赋值、类尾 `static {}` 赋值，可见性给最小。
10. **一次改动不重排别人的代码**：不顺手调格式、改名、挪位置。

**类型与命名**

11. **对象变量用类型名**：`loginLogSummaryRow`，不用 `row`/`data`/`result`（兜底别名可保留语义名）。
12. **类名后缀表达分层**：`Controller`/`Service`/`ServiceImpl`/`Dao`/`Mapper`/`Util`/`Enum`/`Config`；数据载体按流向选 `DTO`（入参）/`VO`（出参）/`Query`/`BO`。**语义已清楚就不硬加**（`OrderResult` 优于 `OrderResultVO`）。
13. **工具先找现成**：项目 util → JDK → hutool/Guava/Commons → 最后自己写。判空**一律用工具**（`CollUtil`/`StrUtil`/`ObjectUtil`），**没有卫语句例外**——`if (x == null) return` 也要写成 `ObjectUtil.isNull(x)`。自造 util 必须 Javadoc 说明标准库为何不满足。
14. **现代 API 优先**：stream / Optional / removeIf / computeIfAbsent / merge。**前提两个同时满足**：可读性不降 + lambda 内无副作用。
15. **并发按场景**：多个独立 IO 明显串行（>500ms 且有实测）才上；自定义线程池，**禁止 `ForkJoinPool.commonPool`**；说不出省了多少毫秒就不加。⚠️ MyBatis `SqlSession` 与 Spring 事务绑 ThreadLocal，异步会脱事务。
16. **字段一律包装类**（Entity/DTO/VO/BO 全用，防静默填 0）；方法内三问——可能为 null？要用包装类 API？要对接泛型/Optional？全否 → 用基本类型。包装类算术前防拆箱 NPE，比较用 `equals`。
17. **循环**：需要跨轮复用的对象（`StringBuilder`/`Pattern`/`DateTimeFormatter`/累加值）提到循环外；单轮局部变量**就地声明**；能用 stream 表达优先用。优化顺序固定：**SQL 与索引 → 减少往返 → 裁列裁行 → 最后才是循环内细节**；循环里查库（N+1）最致命。

**结构与分包**

18. **数据载体与业务逻辑分包**：域下建 `model/`（只放数据），枚举放 `enums/`；不建 `util`/`constant`/`interface` 这类按语法形态分的大杂烩包。
19. **不建内部类**：数据载体一律独立文件（严格私有、只服务外层一个类的实现细节除外）。
20. **协议取值用枚举**：`enums/` 包，`static {}` 建 `CODE_MAP` 查找表，**不要在 `of()` 里遍历 `values()`**。不枚举化两类：表字段映射（要拼 SQL）、纯阈值（TTL/MAX_TOKENS）。
21. **参数 >3，或同组参数在 ≥3 个方法重复 → 建上下文对象**。它只装「这次请求的事实」，不装业务规则。
22. **SQL 一律落 MyBatis XML**，Java 源码禁止拼 SQL 字符串；「就拼一次」也要落 XML，参数走 `#{}`。
23. **不用 Map 套 Map 装业务数据**，建 model 类。仅两处豁免：key 由数据决定的动态列、平台 API 原始返回（边界处一次性转实体）。

---

## 3. 通用铁律（8 条）

1. **先读后写。** 没看过同类代码就动手 = 给项目留第二种风格。禁止凭记忆补 API、凭感觉猜字段名。
2. **最小改动。** 只改必需的行，不顺手格式化/改名/升依赖。
3. **跟随现有风格。** 项目用 `Result<T>` 就用它；项目用字段注入就别改构造注入。**服从现状，不服从「最佳实践」。**
4. **不新增依赖。** 标准库或已有依赖能解决就不引包。
5. **不为一次调用造抽象。** 没有第二个调用点，不抽接口/工厂/策略/Manager。
6. **不吞异常。** 空 `catch` 一律不合格。
7. **不虚报完成。** 没编译不说「通过」，没跑不说「已验证」。
8. **注释写「为什么」。** `// 设置用户ID` 直接删。

---

## 4. 数据载体：禁止裸动态容器

`List<Map<String, Object>>`、裸 `dict`、`Record<string, any>`、`map[string]interface{}` —— **默认不合格**。

| 语言 | 禁止 | 该写成 |
|---|---|---|
| Java | `List<Map>` / `Map` 当入参或返回 | Entity / VO / DTO |
| Python | 裸 `dict` 表示业务对象 | `dataclass` / `TypedDict` / Pydantic |
| TypeScript | `Record<string, any>` / `any` | `interface` / `type` |
| Go | `map[string]interface{}` | struct |

- **判据**：key 在写代码时是否已知？已知 → 必须建类型；未知（列集由配置决定）→ 允许，但泛型写全 + 注释说明原因 + 在边界内消化，不许传到对外接口。
- **泛型能写全就写全**：`BaseRespResult<LoginLogSummaryResult>`，禁止裸 `List` / `Map` / `BaseRespResult` 一路往上传。
- 完整讨论（含为什么、唯一豁免场景、自查清单）见 `references/java-backend.md` 第 10 节。

---

## 5. 语言要点（细节见分册）

| 场景 | 一句话要点 | 分册 |
|---|---|---|
| Java / Spring | Controller 只接参返回、Service 管事务、Mapper 管数据 | `java-backend.md` |
| SQL Server | 显式 `JOIN...ON`；大表 `EXISTS` 优于 `IN`；重复子查询抽 CTE | `sql.md` + `sql-dialects.md` |
| 链式 / Stream | 集合批处理用 Stream；单次查找别用；lambda 不许有副作用 | `style-chain.md` |
| Vue 2 前端 | **存量维护**；组件 ≤300 行；`v-for` 必带业务 key；定时器/echarts 必须销毁 | `frontend-vue2.md` |
| 接口设计 | 统一 `BaseRespResult`；**成功码是 `"1000"` 不是 200** | `api-design.md` |
| Git 提交 | 一个提交一件事；`type: 中文描述`；两个仓库别混 | `git-convention.md` |
| JE 平台 | `ConditionsWrapper` 能力边界、`selectSql` 的坑、多表必须手写 SQL | `je-platform.md` |

---

## 6. 验证纪律

| 项目 | 最低验证 |
|---|---|
| Java/Maven | `mvn -q compile`，涉及逻辑再 `mvn -q test` |
| Java/Gradle | `./gradlew compileJava -q` |
| Python | `python -m py_compile <file>`，有测试跑 `pytest -q` |
| Node/TS | `npx tsc --noEmit` 或 `npm run build` |
| 前端页面 | 起服务实际打开看一次 |
| SQL | 测试库先 `SELECT` 验数，改数据前备份/事务 |
| Shell | `bash -n` 语法检查 + 小样本试跑 |

**汇报三态**：已验证（贴命令+输出）/ 部分验证（说清边界）/ 未验证（说明原因）。
「应该能跑」「逻辑上没问题」「已优化」——禁止出现。

---

## 7. 汇报格式（强制）

```
改了什么：<文件 → 具体变更，一行一个>
为什么：<对应需求/根因>
验证：<命令 → 结果>  或  「未验证：<原因>」
风险/遗留：<未覆盖的分支、需人工确认的点>
```

有 3 个文件改动就列 3 行，不写「优化了多处逻辑」。

---

## 8. 分册索引

**按场景只读该读的那一份。**

| 场景 | 分册 |
|---|---|
| 要细究某条 P0、判断自己的写法算不算违规 | `p0-detail.md` |
| 写/改 Java 后端 | `java-backend.md` |
| 写/改 JE 平台的数据访问、Controller | `je-platform.md` |
| 写/改 SQL | `sql.md`（方言 `sql-dialects.md`） |
| 写/改 Vue 2 前端页面 | `frontend-vue2.md` |
| 新增或改接口 | `api-design.md` |
| 提交代码、写 commit message | `git-convention.md` |
| 链式 / Stream / Optional 风格 | `style-chain.md` |
| 要看反面案例、验证细节 | `anti-patterns.md` |
| 用户要求 review diff/MR | `review.md` |
| 用户要求安全审查 | `security-review.md` |
| 写 Web 代码需安全基线 | `security-general.md` → `security/<lang>-<framework>-<stack>-security.md` |
| 用户直接要求调试/定位根因 | `debug.md` |
| 用户完整原始规则（含需求处理偏好） | `user-rules.md` |

---

## 9. 边界

- 专用报表模板（如 `.rpx`）解析 → 用对应的报表解析工具，本文只约束里面的 SQL 写法。
- Office 文档/表格生成 → 用对应 Office 技能。
- 本文管：**代码怎么写、怎么改、怎么审、怎么验证**。
