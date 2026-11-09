# P0 硬规则 · 完整解释

> 本文件是 `CODING.md` 第 2 节的完整版：每条规则的详细解释、判据、代码示例都在这里。
> 主文件只保留 23 条速查清单；**要细究某条规则，或者不确定自己的写法算不算违规时，读这份**。

---

### 1. 方法 ≤ 80 行，单一职责
校验 / 主逻辑 / 清理 三段分层。

### 2. 主方法保持叙事性
3~7 步调用，或 ≤ 40 行。**不是越短越好**——拆成 5 个 3 行函数，读的人要跳五次。

同一件事的另一面是**抽象层次一致**：方法体只能在一个层次上叙述。判据——把每行换成一句话，能不能连成一段通顺的话？前半段在「复制对象」、后半段突然在「校验字符串格式」，就是层次跳了；把后者抽成一个有名字的方法，主方法就只剩叙述。

### 3. 拆分三问（全不满足就内联）
1. 会被复用吗？
2. 超过 20 行、或含复杂嵌套，值得给个名字吗？
3. 函数名能自解释吗？

三条都否 → **内联，禁止纯传话筒函数**（`doXxx()` 里只有一行转发）。

### 4. 链式适度
- **适合**：`StringBuilder`、`Promise`、`Stream`、`Builder`
- **不硬包**：单条件 `if` 别为了"风格统一"塞进链式
- **底线**：禁止为了链式牺牲可调试性

### 5. 嵌套 ≤ 2 层，卫语句提前 return
超了必须用 guard clause 拍平，不许往右一直缩进。

### 6. 命名硬性

集合变量必须带类型后缀：

| 类型 | 后缀 | 例 |
|---|---|---|
| 列表 / 数组 | `xxxList` / `xxxArr` | `orderList`、`idArr` |
| 映射 | `xxxMap` / `xxxObj` / `xxxDict` | `userMap`、`configDict` |

- 变量名自解释，**禁止** `a` `b` `c` `m` `ev`
- **豁免**：JSON / SSE 等协议字符串的 key 不算变量名
- ⚠️ **全局替换重命名防子串误伤**：`rows` → `rowList` 会把 `throws` 变成 `throwrowList`。替换后**必须编译验证**

### 7. 集合返回空，不返回 null
`Collections.emptyList()` / `[]`。不把判空负担甩给每个调用方。

### 8. 日志与异常
- 日志用**占位符 / 结构化参数**，不拼字符串：`log.info("user {}", userId)`
- `catch` 必须打**带上下文**日志，**禁止吞异常**
- 对外错误消息用中文；技术细节（堆栈、内部标识）进日志
- **Controller / Service 默认不包兜底 try-catch**：平台有全局异常处理器时（先查项目里有没有 `HandlerExceptionResolver` / `@ControllerAdvice`），让异常往上抛，由它统一转成错误响应；主方法包一层"catch 完 errorResult"属于和全局处理器重复，堆栈还会打两份。只有要**翻译异常语义**（技术异常 → 业务提示）、**降级返回默认值**或**释放资源**时才 catch，且 catch 里必须有上下文日志

### 9. 常量与注释
- 魔法值常量化
- **公共函数**写 Javadoc / docstring：用途、参数、异常
- **函数体内**注释只写「为什么」，不写「做什么」

**常量放哪里**（2026-11 修订，解决「业务类头堆一堆 static」）：

| 情形 | 落位 |
|---|---|
| 多个类共用的协议值（SSE 事件名、状态码、指令码） | **独立常量类**，单一来源 |
| 只服务一个类 | 留在该类，`private` |
| 类头常量 > 5 个且分属不同职责（协议 / 提示词 / 阈值） | 按职责拆出去，不许全堆类头 |
| 有限、封闭的取值集合（操作码、意图、状态机状态） | **用枚举**，见第 20 条 |

- **可见性给最小**：`public` 而零调用方的常量 = 误导后来者以为有外部契约
- **赋值方式（2026-11-06 修订，用户既定习惯）**：常量**声明处一律不赋值**，统一在类尾 `static {}` 块内赋值。声明处保留 Javadoc；类型选择见第 16 条（static final 常量用基本类型，String 除外）

### 10. 一次改动不重排别人的代码
只动自己改的那个方法。不顺手调格式、不顺手改名、不顺手挪位置。

### 11. 对象变量用类型名，不用泛化短名
`new` 出来的对象，变量名取**类型名首字母小写全拼**；禁止 `row` / `obj` / `data` / `item` / `result` 这类泛化名。

```java
✅ LoginLogSummaryRow loginLogSummaryRow = new LoginLogSummaryRow();
✅ for (LoginLogSummaryRow loginLogSummaryRow : rowList) { ... }
❌ LoginLogSummaryRow row = new LoginLogSummaryRow();
```

- 集合仍按第 6 条走 `xxxList` / `xxxMap`，**不要**写成 `loginLogSummaryRows` / `loginLogSummaryRowList`
- 例外：`Type x = a == null ? new Type() : a` 这种**兜底别名**可保留语义名（如 `safeQuery`）
- 其他语言同理：Python `login_log_summary_row = LoginLogSummaryRow()`、TS `const loginLogSummaryRow = new ...`

### 12. 类名后缀表达分层，冗余的别加
**职责类必带后缀**（少了就等于没分层）：
`XxxController` / `XxxService` / `XxxServiceImpl` / `XxxDao` / `XxxMapper` / `XxxUtil` / `XxxEnum` / `XxxConfig`

**数据载体按流向选后缀**：
| 后缀 | 用途 |
|---|---|
| `XxxDTO` | 入参 / 跨层传输 |
| `XxxVO` | 出参 / 展示 |
| `XxxQuery` | 查询条件 |
| `XxxBO` | 领域内部组合体 |

- **语义已经说清职责时不硬加**：`LoginLogSummaryRow`、`OrderResult` 比 `LoginLogSummaryRowVO`、`OrderResultVO` 更好读
- 判据：**后缀能不能让调用方少猜一层？** 不能就删掉
- 禁止同义后缀并存：`UserManager` 与 `UserService` 二选一，不要两个都造

### 13. 工具先找现成的，别手写
查找顺序：**项目内已有 util → JDK / 框架自带 → hutool / Guava / Apache Commons → 最后才自己写**。

- 本仓库后端已依赖 **hutool 5.8.12**：`StrUtil`、`NumberUtil`、`LocalDateTimeUtil`（5.8 还没有 `LocalDateUtil`）、`CollectionUtil`、`JSONUtil`、`BeanUtil`、`IoUtil`
- 平台自带 `com.je.core.util.StringUtil`、`O2S` 等，别在业务里重写 `isEmpty` / 类型转换
- 判据：**要写的方法在 hutool / Commons 里有同名实现 → 用现成的**；只有带业务语义的（本项目特有口径）才进 `XxxUtil`
- 其他语言同理：Python 用 `pathlib` / `itertools` / `collections`，JS 用原生 `Array.prototype.*` 或项目已装的 lodash；禁止手写 `isBlank` / `deepClone` / `formatDate`
- 自造 util 必须写 Javadoc 说明**为什么标准库和第三方都不满足**

**判空 / 兜底一律用工具，不写裸比较**（Java）：

| 类型 | 用这个 | 不要写 |
|---|---|---|
| 集合 / Map | `CollUtil.isEmpty` / `isNotEmpty` / `emptyIfNull` | `list == null \|\| list.isEmpty()`、`list == null ? emptyList() : list` |
| 字符串 | `StrUtil.isBlank` / `isNotBlank` / `emptyToDefault` | `str == null \|\| str.trim().isEmpty()` |
| 包装类 / 任意对象 | `ObjectUtil.isNull` / `isNotNull` / `defaultIfNull` | `obj == null ? a : b` |
| 数字取值 | `NumberUtil.parseInt` / `toInt` / `round` | 手写 `Integer.parseInt` + try-catch |
| 对象 → long/double 带兜底 | `Convert.toLong(obj, 0L)` | 手写 instanceof + parse + catch |

- **2026-11-06 强化（用户显式要求）**：判空用工具**没有卫语句例外**——`if (obj == null) return;` 也要写成 `if (ObjectUtil.isNull(obj)) return;`。查所有裸 `== null` / `!= null` 都算违规（唯一豁免：`instanceof` 类型判断、协议 JSON key）
- 例外：**数值格式解析失败的预期分支**可以静默降级，但 catch 里必须带注释说明为什么
- 其他语言对应写法：Python `if not lst` / `value or default`；JS/TS `??` / `?.` / `Array.isArray(x) && x.length`（或 lodash `isEmpty`）

### 14. 现代 API 优先，但不为准而牺牲可读性
- Java 8+：`stream().filter/map/max/min/sum/count/groupingBy`、`Optional`、`removeIf`、`computeIfAbsent` / `computeIfPresent`、`Map.merge`
- **必须同时满足两个前提**：可读性不下降 + lambda 内无副作用

```java
✅ rowList.stream().filter(r -> r.getLoginCount() > 0)
        .max(Comparator.comparingInt(LoginLogSummaryRow::getLoginCount)).orElse(null);
❌ list.forEach(r -> resultList.add(r));        // lambda 里有副作用，改 for
❌ 3 行 for 硬拆成 3 层 stream 链               // 可读性下降
```

- 其他语言同理：Python 用推导式 / 生成器表达式，JS 用 `map` / `filter` / `reduce`，判定标准一样

### 15. 并发按场景用，不是按"高级"用
- **该用**：多个相互独立的 IO 明显串行拖慢接口（>500ms，且有实测数据）、批量任务、确有共享可变缓存
- **工具**：`CompletableFuture` + **自定义线程池**（禁止裸用 `ForkJoinPool.commonPool`）、`ConcurrentHashMap` / `AtomicXxx`、读写锁只保护真正共享的可变状态
- **不该用**：Spring 单例但无共享可变状态、几次轻量查询（<100ms）、只为让代码"看起来高级"
- ⚠️ **本项目硬约束**：MyBatis `SqlSession` 与 Spring 事务都绑在 ThreadLocal 上，异步线程里直接复用会**脱离事务上下文**；要异步操作数据库必须重新取连接或显式传递上下文
- 判定话术：说不出"省了多少毫秒 / 解决了哪个竞态"，就不加锁、不加异步

### 16. 字段一律包装类；方法内按场景选包装类或基本类型
- **类的字段（属性）一律用包装类**：Entity / DTO / VO / BO 全部如此，哪怕它"看起来不可能为空"（自增主键、计数、状态码）。类实例经常是 ORM / JSON 反序列化出来的半成品，基本类型会被**静默填成 0**，脏数据就这样混进业务
- **方法内的局部变量按三问判断**，命中任一就用包装类：
  1. **可能为 null 吗？**（例如"未登录天数"用 null 表示从未登录，不能用 0）
  2. **需要包装类的 API 吗？**（`parseInt` / `compareTo` / `toString` / `NumberUtil` 入参）
  3. **要跟包装类字段、泛型集合、`Optional` 对接吗？**（省得在边界上反复拆装）
  - 三问全否 —— 纯算术中间值、循环计数、必然非空的计算结果 → **用基本类型**，免装箱、免拆箱 NPE、读数更直接
- 用包装类时守住三条安全约束：
  1. **算术前确保非空** —— `a - b` 会自动拆箱，任一为 null 直接 NPE，且 NPE 落在表达式中间极难定位；入口用 `ObjectUtil.defaultIfNull` 兜底，或先判空再算
  2. **比较用 `equals` / `Objects.equals`**，禁止 `==`（`Integer 128 == Integer 128` 是 false）
  3. **装箱只发生在赋值 / 传参处**，不要在循环里对同一个值反复装箱
- **必须用基本类型的场景**：`for (int i = 0; ...)` 循环计数器与数组下标（语法要求 int）、`switch case`、`static final` 常量、第三方 API 签名要求基本类型时
- 一句话判据：**"这个值会不会为空 / 要不要用它的方法？"** 会或要 → 包装类；都不会 → 基本类型
- 包装类参与算术会自动拆箱，依赖 SQL / 上游保证非空时，必须在类 Javadoc 里写明"非空契约"
- 其他语言：Python 注意 `None` 与 `0` 的区别，JS 无 int/包装类之分，规则落在"**可空性必须显式表达**"

### 17. 循环与性能：声明提到循环外，但别指望它省内存

> **适用边界（2026-11 修订）**：只对**需要多轮复用或累计**的对象提前声明——`StringBuilder`、`Pattern`、`DateTimeFormatter`、跨轮累加值、结果集。
> 单轮内算一次的局部变量**就地声明**：提到循环外会在方法头堆出一片空声明（`String op; JSONObject obj;`），读的人要往下找才知道它是什么，比「每轮 new」更难读。
> 能表达成集合处理时优先用 `stream / 列表推导`（`filter` 替代 `continue`、`map` 替代赋值、`collect` 替代 `add`），此时根本不存在这个问题。

- **团队约定**：循环体用到的变量**在循环外声明、循环内只赋值**（类型仍按第 16 条的三问判断）
  - 硬约束：**每轮必须先赋值再使用**；某一轮分支跳过赋值，就会带上上一轮的残留值（这是提前声明唯一真实的风险）
  - `for (Xxx item : list)` 的迭代变量受语法限制提不出去，不用管
  - 提前声明**不会减少对象分配**（局部变量本来就在同一栈槽里复用），它的价值是"一处集中声明、一眼看清这个方法用了哪些变量"，属于**可读性约定，不是性能优化**
- **循环内真正贵的是**：字符串 `+` 拼接、`new SimpleDateFormat`（还线程不安全）、`Pattern.compile`、`String.format`、未预估容量的 `ArrayList/HashMap`、**枚举 `values()`（每次调用都克隆一份数组）**，以及最致命的**循环里查库/调 RPC（N+1）**
  - 这类对象必须提到循环外复用：`StringBuilder`、`Pattern`、`DateTimeFormatter`、复用前要 `clear()` 的 `List`/`Map`、跨迭代累计值
- 优化顺序固定为：**SQL 与索引 → 减少往返次数 → 裁掉不用的列和行 → 最后才是循环内细节**
- "考虑并发"先答三个问题：有没有共享可变状态？单请求内存多大（结果集行数 × 行宽）？每请求几次 IO？答不上来就别加锁、别上线程池

### 18. 数据载体与业务逻辑分包
每个业务域下建 `model`（或 `dto` / `vo` / `entity`）子包，**数据载体不许和 Service / Handler 平铺在同一层**。

```
report/
├── ReportService.java       业务编排
├── model/                   只有数据，不含业务逻辑
│   ├── ReportTemplate.java
│   └── ReportChatPlan.java
└── chat/                    业务逻辑
    └── ReportChatService.java
```

- **按角色分包（数据 / 逻辑 / 协议）**；不要建 `util` / `constant` / `interface` 这类按语法形态分的大杂烩包，那会把同一块业务切到五六个包里
- **枚举是唯一例外**：统一放域下 `enums` 子包（如 `application/report/enums/`），不跟 Service 混放。**别管别的模块建不建，我们建**
- 被 `model` 内其他类引用的类型（例如 Plan 的字段是个枚举）必须一起挪过去，否则形成 `model → 业务包` 的倒置依赖

### 19. 不建内部类
数据载体一律独立文件，不用 `static class` 塞进业务类里。
- 理由：内部类让「这个类有哪些职责」看不清；且它隐式访问外层私有字段，抽出来时容易漏改
- 例外：严格私有、只被外层一个类使用的实现细节（如缓存条目）可以保留——抽出去在多占一个文件与收益之间不划算
- 抽离必检：`outer.privateField` 这类隐式访问要改成 getter，编译器会报错，别忽略

### 20. 协议取值集合用枚举
有限、封闭的取值集合（操作码、意图、状态机状态）用**枚举**，不要用一串 `static final String`。
- **落位**：统一放域下 `enums` 子包（如 `application/report/enums/`）。**别管别的模块建不建，我们建**——这是团队约定，不是看齐现有代码
- 用 `static {}` 建 `CODE_MAP` 查找表；不要在 `of()` 里遍历 `values()`（每次调用都克隆数组）
- `switch` 换成枚举后，case 拼错编译期即报错；保留 `default` 兜底，防止枚举后续扩展漏改 case 被静默吞掉
- **不要枚举化这两类**：表字段映射（要拼进 SQL 字符串，枚举化只会让拼接更啰嗦）、纯阈值（MAX_TOKENS / TTL）

### 21. 参数搬运 → 上下文对象
同一组参数在 3 个以上方法重复出现，或单方法参数 > 3 个 → **建上下文对象**。
- 典型症状：十个 handler 全是 `(service, payload, listA, listB)` 同一个签名；调用点要数着位置传
- 上下文可以持有 IO 出口（`Consumer` / `Writer` / `Response`），把「什么时候发」留给业务方法，「事件长什么样」收进上下文
- 上下文只装「这次请求的事实」，不装业务规则——它是参数容器，不是垃圾桶

### 22. SQL 一律落 MyBatis XML，Java 里不拼 SQL 字符串（2026-11-06 新增）
Java 源码（含 Service / Util / 查询组件）里**禁止出现拼出来的 SQL**——字符串 `+` 拼 WHERE、
`escapeSqlLiteral` 手工注入防护都算。查库只有两条路：
1. **MyBatis mapper**：Dao 接口（`@Mapper`，包路径进 MapperScannerConfigurer 的 basePackage，
   本仓库业务模块是 `com.example.order.dao`）+ `resources/mapper/XxxDao.xml`；SQL 参数一律 `#{}` 占位
2. **单表动态条件**：`ConditionsWrapper` 链式（见第 5 节）
- 简单的一次性查询**也要落 XML**——「就拼一次」是烂掉的开端；日期等外部值必须走 `#{}` 参数，
  不许字符串连接进 SQL
- 历史基建（如某个遗留的 Jdbc 拼接执行类）保持原样不改，但**新代码禁止新增调用**

### 23. 数据结构不用 Map 套 Map，用实体类（2026-11-06 新增）
`List<Map<String, Object>>` / `Map<String, Map<String, Object>>` 装**业务数据**一律不合格，
建 model 类（Lombok `@Data`，数据载体进 `model/` 包，见第 18 条）。SSE / JSON 协议的**载荷**
同样建实体类；仅两处豁免：① key 由数据决定的动态列（如「场名 → 值」），② 平台 API 的原始返回
（必须在边界处一次性转成实体）。

### 语言细则
- **Java**：`List` 变量以 `List` 结尾、`Map` 以 `Map` 结尾、常量 `private static final`
- **JS/TS/Vue**：常量 `UPPER_SNAKE_CASE` + `const`，模板字符串不用 `+` 拼接
- **Python**：`list` 变量 `xxxList`、`dict` 变量 `xxxDict`、用 docstring
- **通用**：对象变量见第 11 条、类名后缀见第 12 条、复用工具见第 13 条、高阶 API 见第 14 条、并发见第 15 条、类型选择见第 16 条、性能定位见第 17 条、分包见第 18 条、内部类见第 19 条、枚举见第 20 条、参数上下文见第 21 条 —— 这几条**与语言无关**，写 Python / Vue / JS 同样适用
