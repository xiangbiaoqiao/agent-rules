# JE 平台开发要点

> 本项目跑在 JE 平台上，数据访问和 Controller 写法与普通 Spring 项目**不一样**。
> 下面这些是踩过坑之后固化的结论，写后端代码前必读。

---

**Spring 接口层写法**

⚠️ **本项目现状（2026-11 核实）**：绝大多数 Controller 是 `@Controller` + 方法上 `@ResponseBody`，
并 `extends AbstractPlatformController`，依赖注入用**字段 `@Autowired`**。

**新建 Controller 跟随同模块现状**——P1（项目现状）优先于 P2（框架惯例）。不要为了「更现代」改成
`@RestController` + 构造注入，那样会让同一个模块里出现两种风格，下一个维护的人要先判断哪套是主流。

在此基础上，能省的照省：

- 请求方法用 `@GetMapping` / `@PostMapping`，不要 `@RequestMapping(method = RequestMethod.POST)` 长写法
- 单个路径变量用 `@PathVariable` 简写；参数绑定用对象接（>3 个参数建 DTO），不要一长串 `@RequestParam`
- 只有要返回 JSP / 视图 / 重定向时才**必须**用 `@Controller` + `@ResponseBody`

**SQL 落位判据**（项目里有 `MetaService` + je-ibatis 的 `ConditionsWrapper` 时，别为一条固定 SQL 开 Dao 方法）：

**一句话：单表能用链式就用链式；一旦要多表关联，老老实实写 SQL。**

| 场景 | 落位 | 备注 |
|---|---|---|
| **单表** + 纯条件（且有动态条件需求） | `ConditionsWrapper` 链式 + `metaService.select(tableCode, wrapper)` | 不写 SQL 字符串、不开 Dao 方法 |
| **需要 `DISTINCT` / 列别名 / 表达式 / 多表 JOIN / CTE** | **手写完整 SQL** | 有动态条件或要复用 → Dao + XML；一次性 → `ConditionsWrapper.builder("完整SQL")` + `selectSql` |
| 动态条件 / 参数复用 / 分页 | Dao + XML | `<where>` / `<if>`，返回 VO 不返回 Map |

单表链式（**必须配 `select(tableCode, wrapper)`**）：

```java
ConditionsWrapper userWrapper = ConditionsWrapper.builder()
        .isNotNull(true, "EXECUTIVENAME")
        .ne(true, "EXECUTIVENAME", "")
        .orderBy(true, true, "EXECUTIVENAME");
List<DynaBean> userBeanList = metaService.select("JE_CORE_ENDUSER", userWrapper);
```

需要别名 / `DISTINCT` 时，链式给不了，直接写完整 SQL：

```java
ConditionsWrapper jobWrapper = ConditionsWrapper.builder(
        "SELECT DISTINCT EXECUTIVENAME AS jobName"
                + " FROM JE_CORE_ENDUSER"
                + " WHERE EXECUTIVENAME IS NOT NULL AND EXECUTIVENAME <> ''"
                + " ORDER BY jobName");
List<Map<String, Object>> jobRecordList = metaService.selectSql(jobWrapper);
```

⚠️ **`selectSql` 只认"完整 SQL"，不会帮你拼 `SELECT` / `FROM` / `WHERE`**（它的 mapper 是空的 `<if test="1==1"/>`，SQL 全部取自 wrapper）。把 `selectColumns` / `table` / `isNotNull` 这类**链式片段**丢给 `selectSql`，会拼出缺 `WHERE` 的语句而炸：

```
SQL: EXECUTIVENAME IS NOT NULL AND EXECUTIVENAME <> ? ORDER BY jobName ASC
错误：关键字 'IS' 附近有语法错误
```

（2026-11-05 登录日志汇总表职务下拉真实踩过。另注：`select(tableCode, wrapper, columns)` 的 `columns` 参数在 `MetaServiceImpl` 里**根本没被使用**，别指望它传列。）

⚠️ **多表别去找链式 join API —— 它不存在，别再花时间翻：**

- `ConditionsWrapper` 的能力边界只有：where 类条件（`eq` / `ne` / `gt` / `like` / `in` / `between` / `exists` …）、`nested` / `and` / `or`、`groupBy`、`orderBy`、`apply`、`selectColumns`、`table` / `app`（动态表名占位符）。**没有任何 `leftJoin` / `innerJoin` / `rightJoin`，也没有 ON 条件构造。**
- 它 `implements Join<ConditionsWrapper>`，但 **`Join` 接口是 MyBatis-Plus 的历史命名失误**：接口里只有 `or()` / `apply()` / `applyBefore()` / `exists()` / `notExists()`，**与 SQL JOIN 毫无关系**。看到 `implements Join` 不要以为能关联表。
- MyBatis-Plus 原生同样不提供 join API（官方立场：多表请写 SQL）。社区的 `mybatis-plus-join`（MPJ）挂在 MP 的 `BaseMapper` / `TableInfo` 体系上，**与 JE 平台的 `MetaService` + `DynaBean` + 动态表名机制不兼容，不引入**。
- 实证：本仓库 Java 源码搜 `leftJoin|innerJoin|rightJoin` **命中 0 次**，多表一律 XML 手写。这不是将就，是既定范式。

**`apply` / `builder(String, ...)` 塞的是"裸 SQL 片段"，塞 where 还是塞整条 SQL 取决于入口**（两者等价：`builder(s, args)` 内部就是 `new ConditionsWrapper().apply(s, args)`）：

| 入口 | 片段落点 | 例 |
|---|---|---|
| `metaService.select(tableCode, wrapper)` | 平台拼 `SELECT ... FROM tableCode`，片段进 **where 区** | `builder("JE_CORE_USERINFO_ID = {0}", id)` |
| `metaService.selectSql(wrapper)` / `selectSql(sql, params)` | **直接执行**片段，可整条 `SELECT` | `selectSql("SELECT a.x FROM a LEFT JOIN b ON ...", param)` |

- `selectSql` 返回 `List<Map<String, Object>>`，字段名靠字符串、无编译期检查（违背第 4 节）。**只用于一次性、结构简单的查询**；要稳定复用或有动态条件的多表查询，走 Dao + XML 返回 VO。
- 集合返回值永远不要 null：`CollUtil.emptyIfNull(x)`（等价于 `Optional.ofNullable(x).orElse(emptyList())`，更短）

