# 代码质量铁律与反面案例

这份是主规范，其他 reference 都是它的补充。**每次写代码前过一遍第 1 节，交付前过一遍第 5 节。**

> ⚠️ **先读 `~/.agent-rules/CODING.md`（P0）。** 那份是权威规则，优先级高于本文件的一切建议。本文件负责它没覆盖到的部分：案例细节、验证命令矩阵、虚构与动态容器的具体表现。

---

## 1. 动手前的 60 秒：读现场

在写第一行代码之前，必须完成这四件事。少一件都不许动手。

| # | 动作 | 具体做什么 |
|---|---|---|
| 1 | 读被改文件全文 | 不是读 diff 片段，是读整个文件。不知道文件多大就用行数先看，超过 500 行也至少读完相关的类/方法块 |
| 2 | 读同目录 2–3 个同类文件 | 抄它们的：包路径、类注解、注入方式、返回包装、异常抛法、日志格式 |
| 3 | 找可复用的东西 | 项目里已有的：工具类、常量类、枚举、Result 包装、分页对象、日期处理、断言。**先找到，再决定要不要新写** |
| 4 | 确认改动面 | 列出「要改的文件 → 每个文件改什么」。超过 3 个文件，先跟用户确认 |

### 为什么这条排第一

AI 写代码最容易犯的错不是写错逻辑，是**写出一个和项目格格不入的平行世界**：项目用 `Result.success()`，它返回裸对象；项目用 `@RequiredArgsConstructor`，它写 `@Autowired` 字段；项目 mapper 叫 `listXxx`，它造 `selectAll`。功能能跑，但项目从此有两种风格，后续每个人都要多读一次脑子。

**风格服从现状，不服从"我觉得更好"。** 想改风格，那是单独的、用户明确要求的重构任务。

---

## 2. 最小改动原则

### 硬规则

- 只改完成任务**必需**的行。想改旁边那行不规范的代码？**先问。**
- 不做顺手重命名、顺手调格式、顺手优化性能、顺手升依赖版本。
- 不为了"让代码更整齐"而移动方法位置（diff 会变得无法 review）。
- 不删除看起来没用但你没确认调用点的代码。删之前 `grep` 全项目。

### 反面案例

```diff
- // 需求：给查询加一个状态过滤
- public List<Order> list(Long userId) {
-     return orderMapper.selectByUserId(userId);
- }
+ public Result<PageResult<OrderVO>> list(Long userId, OrderQueryDTO dto) {
+     // 一口气改了签名、换了返回类型、加了分页、抽了 VO、顺手把 userId 改成了 Long[]...
+ }
```
需求只是「加状态过滤」，结果是 Controller/Service/Mapper/前端全要跟着改。这是最典型的过度改动。

正确做法：
```diff
  public List<Order> list(Long userId) {
-     return orderMapper.selectByUserId(userId);
+     return orderMapper.selectByUserId(userId, status);
  }
```
只加一个参数，其余不动。

---

## 3. 不造抽象

### 判定：这个抽象有第二个使用者吗？

- 没有 → **内联，不抽。**
- 有 → 再问：抽出来的名字能准确描述**业务含义**吗？不能 → 内联。
- 只是"纯技术工具"（如 `isBlank`、`getStringIgnoreCase`）→ 放 util，允许。

### 明确禁止

| 反模式 | 说明 |
|---|---|
| 单实现的接口 | `OrderService` + `OrderServiceImpl` 是 Spring 惯例，可以；但为一个方法造 `OrderHandler` 接口 + 唯一实现类，不行 |
| 一次性工厂 / 策略 | 只有一个分支的策略模式，等于 `if` 加两层跳转 |
| `XxxManager` / `XxxHelper` / `XxxUtil2` | 命名含糊的垃圾桶类，会把逻辑越堆越乱 |
| 三层 DTO 转换 | `Entity → PO → DTO → VO` 只是字段搬运，没有语义差异就砍掉 |
| 万能基类 | `BaseController<T, Q, V>` 省下的样板代码，抵不过理解成本 |

### 方法长度

- 单方法 **≤ 80 行**，校验 / 主逻辑 / 清理 三段分层。
- 主方法保持**叙事性**：3~7 步调用，或 ≤ 40 行。**不是越短越好**——把 20 行拆成 5 个 3 行函数，读的人要跳五次，反而更差。
- **嵌套 ≤ 2 层**，超了用卫语句提前 `return`，不许一路往右缩进。
- **拆分三问**（全不满足就内联）：会复用吗？>20 行或含复杂嵌套值得给名字吗？函数名能自解释吗？三条都否 → 内联，禁止纯传话筒函数。
- 私有方法名必须能准确描述业务：`validateFamc`、`buildXmlxMap`、`validateByType`——不是 `handle1`、`doProcess`、`processData`。

---

## 4. 异常、日志、边界

### 异常

- **禁止空 catch。** 三种合法写法：处理掉（带说明）、包装后抛、打 error 日志后抛。
- 业务异常统一用项目已有的 `BusinessException`（或同类），不要每次 `throw new RuntimeException("xxx")`。
- Controller 层交给全局异常处理器，不写 try-catch 拼装返回。
- 不吞 `InterruptedException` 的 interrupt 标志位。
- 资源用 try-with-resources / `with` / `using`，不靠手写 `finally` 关流。

### 日志

- 关键操作 info，调试 debug，异常 error。**不用 `System.out.println` / `print` / `console.log` 留在业务代码里。**
- 日志必须带业务标识（userId / orderId / batchId），否则线上等于没打。
- 禁止把密码、token、完整身份证/手机号打进日志。

### 边界（写完必过一遍）

null、空集合、空字符串、0、负数、超大值、超长字符串、重复提交、并发、时区、小数精度（金额用 `BigDecimal`，禁用 `double`）。

**每个入参都问一句：如果它是 null / 空 / 负数，这段代码会怎样？**

---

## 5. 验证纪律

> 没有证据的"完成"是撒谎。

| 语言/项目 | 最低验证动作 |
|---|---|
| Java/Maven | `mvn -q compile` → 涉及逻辑再 `mvn -q test` |
| Java/Gradle | `./gradlew compileJava -q` |
| Python | `python -m py_compile <file>`；有测试就 `pytest -q <path>` |
| Node/TS | `npx tsc --noEmit` 或 `npm run build`；有 lint 就 `npm run lint` |
| 前端页面 | 起本地服务，实际打开看一次 |
| SQL | 先在测试库 `SELECT` 验数，再改数据；改数据前备份/事务 |
| Shell | `bash -n` 语法检查，小样本试跑 |

### 汇报必须区分三态

- **已验证**：贴命令 + 关键输出（行数、耗时、返回码）。
- **部分验证**：说清验了什么、没验什么。
- **未验证**：直接说"未编译/未运行"，并说明原因（缺依赖、缺库权限、需人工环境）。

「应该能跑」「逻辑上没问题」「已优化」——这三句一律不许出现在汇报里。

---

## 6. 不许虚构

以下东西**必须**有出处，不许凭印象写：

- 方法名、类名、字段名 → 在项目里 `grep` 到，或 `references/` 里查到
- 第三方库 API → 确认版本内存在（看 `pom.xml` / `package.json` / 已安装包）
- 配置项 key → 在 `application.yml` / `.env` / 配置类里找到
- 数据库表名字段名 → 查 schema 或已有 SQL，不许猜
- 命令行参数 → `--help` 或文档

不确定时：**说"我不确定 X，需要确认"，而不是编一个看起来合理的名字。** 编错的字段名会让用户花半小时排查一个不存在的错误。

### 6.1 同一类逃避：用动态容器糊过去

虚构字段名是「编个假名字」，**裸 `Map` / `dict` / `any` 是「干脆不起名字」**——动机完全一样：不想搞清楚数据到底有哪些字段。

| 语言 | 禁止的写法 | 该写成 |
|---|---|---|
| Java | `List<Map<String, Object>>` / `Map` 当返回值 | Entity / VO / DTO 投影对象 |
| Java | `Map<String, Object>` 当方法入参（>3 个键） | DTO |
| Python | 返回裸 `dict` 表示业务对象 | `dataclass` / `TypedDict` / Pydantic 模型 |
| TypeScript | `Record<string, any>`、`any`、不写返回类型 | `interface` / `type` |
| Go | `map[string]interface{}` | struct |

**判断标准**：这个容器的 key 在写代码时是不是已知的？
- 已知 → **必须建类型**。key 已知还用 Map，就是偷懒。
- 未知（列集由配置/模板决定）→ 允许，但必须写全泛型 + 注释说明原因 + 在边界内消化，不许传到对外接口。

**不知道字段时怎么办**：读表结构、读现有 Entity、读已有 SQL、读接口文档，或者直接问。**不要用 Map 把不确定性糊过去**——糊过去的代价由下一次改代码的人承担。


---

## 7. 语言与格式

- 标识符英文，注释与用户沟通用中文（跟随用户语言）。
- 缩进跟随文件现状；新文件 Java 4 空格、JS/TS 2 空格。
- 单行 ≤ 120 字符（Java）/ 100（JS）。
- 字符串引号：代码内一律 ASCII 直引号 `"` `'`，不用中文引号（会编译报错）。
- 文件编码 UTF-8，换行跟随仓库（Windows 项目注意别把 LF 全改成 CRLF，反之亦然）。
- 提交前不留：`TODO`、`FIXME`、注释掉的死代码、调试日志。

---

## 8. 交付自查表（复制到心里逐条过）

```
[ ] 读过 user-rules.md（P0）
[ ] 读过被改文件全文与 2-3 个同类文件
[ ] 风格与同目录代码一致（注解/注入/返回包装/命名/Mapper 命名）
[ ] 方法 ≤80 行；主方法 3~7 步或 ≤40 行；嵌套 ≤2 层
[ ] 集合变量带 List/Arr/Map/Obj/Dict 后缀；无 a/b/c/m/ev
[ ] 集合返回空而非 null；日志用占位符；catch 有日志
[ ] 没有夹带无关改动
[ ] 没有新依赖 / 新抽象 / 新工具类（或已论证必要）
[ ] 无空 catch、无调试输出残留、无 TODO
[ ] 边界条件已考虑（null/空/0/负/超长/并发）
[ ] 已编译或已运行，命令与结果可复述
[ ] 所有字段名/API/配置项都有出处，无虚构
[ ] 汇报里明确区分了「已验证」与「未验证」
```
