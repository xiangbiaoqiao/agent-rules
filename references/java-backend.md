# Java / Spring Boot 后端规范

融合自 Codex `java-dev`（SKILL.md + conventions.md + spring-boot.md）。
**先做一件事：看项目实际的包结构。下面的结构是默认期望，不是强制真相。项目已有一套就服从项目。**

---

## 1. 分层

```
Controller → Service → Mapper → DB
     ↓          ↓
   DTO/VO    Entity
```

| 层 | 只做 | 绝不做 |
|---|---|---|
| Controller | 接参、`@Valid` 校验、调 Service、返回 `Result<T>` | 写业务逻辑、拼 SQL、try-catch 组装返回 |
| Service | 业务编排、事务边界 | 直接拼 HTTP 响应、依赖 `HttpServletRequest` |
| Mapper | 数据访问 | 业务判断、跨表事务 |

## 2. 新建模块的生成顺序

1. `Entity`（`@TableName` / `@TableId` / `@TableLogic` / `@TableField(fill=...)`）
2. `Mapper`（MyBatis-Plus `BaseMapper<T>` 优先，复杂 SQL 才写 `@Select` 或 XML）
3. `DTO` / `VO`（请求 / 响应分离；不要让 Entity 直接出网关）
4. `Service` 接口 + `impl`
5. `Controller`

## 3. 命名

| 类型 | 规则 | 例 |
|---|---|---|
| 类 | PascalCase | `UserService` `OrderController` |
| 方法/变量 | camelCase | `getById` `userName` |
| 常量 | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| 包 | 全小写连续 | `com.example.user` |
| 查单条 | `getXxx` / `findXxx` | `getById` |
| 查列表 | `listXxx` / `queryXxx` | `listByUserId` |
| 分页 | `pageXxx` | `pageByCondition` |
| 新增 | `insert` / `save` | |
| 更新 | `update` | |
| 删除 | `delete` / `remove` | |

**Mapper 方法名要跟项目现有的一致。** 项目全用 `list*`，你别造 `selectList*`。

### 变量命名（用户 P0 第 6 条，硬性）

| 类型 | 后缀 | 例 |
|---|---|---|
| 列表 / 数组 | `List` / `Arr` | `orderList`、`idArr` |
| Map | `Map` | `userMap` |

- 常量 `private static final` + `UPPER_SNAKE_CASE`
- 禁止 `a`/`b`/`c`/`m`/`ev` 一类命名
- 豁免：JSON / SSE 等协议字符串的 key 不算变量名
- **注意区分**：Mapper **方法名**用 `listXxx`（`listByUserId`），**变量名**用 `xxxList`（`orderList`）——两者不冲突
- ⚠️ 全局重命名防子串误伤：`rows` → `rowList` 会把 `throws` 变成 `throwrowList`，改完必须 `mvn -q compile` 验证

## 4. 类结构顺序

1. 静态常量 → 2. 实例变量 → 3. 构造 → 4. 公共方法 → 5. 私有方法

## 5. Controller 模板

```java
@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/{id}")
    public Result<UserVO> getById(@PathVariable Long id) {
        return Result.success(userService.getById(id));
    }

    @PostMapping
    public Result<Long> create(@Valid @RequestBody UserCreateDTO dto) {
        return Result.success(userService.create(dto));
    }
}
```

要点：`@Valid` + JSR-303 注解做参数校验；统一 `Result<T>` 包装；不写业务逻辑。

## 6. Service

- 接口 + `impl/` 实现类，`@Service`
- 事务：`@Transactional(rollbackFor = Exception.class)`
- 注入：构造注入（`@RequiredArgsConstructor`），**不用字段 `@Autowired`**

## 7. 代码风格

- 缩进 4 空格，不用 Tab；单行 ≤ 120 字符
- Lombok：`@Data` `@Builder` `@RequiredArgsConstructor` `@Slf4j`（项目没用 Lombok 就别引）
- **方法 ≤ 80 行**；主方法保持叙事性（3~7 步调用或 ≤ 40 行），不是越短越好
- **嵌套 ≤ 2 层**，超了用卫语句提前 `return`
- **集合返回空不返回 null**（`Collections.emptyList()`）
- **魔法值常量化**
- 公共方法写 Javadoc（用途 / 参数 / 异常）；函数体内注释只写"为什么"
- 私有方法返回 `null` 表示校验通过、返回错误串表示失败——仅在项目已是这个约定时沿用

## 8. 异常与日志

- 业务异常用自定义 `BusinessException`（或项目已有的）
- 全局异常处理：`@RestControllerAdvice`
- 不吞异常，至少 `log.error("xxx", e)`
- `@Slf4j`；info/debug/error 分级；日志带业务标识（userId / orderId）
- **日志用 `{}` 占位符，不拼字符串**：`log.info("user {}", userId)`，不是 `log.info("user " + userId)`
- **对外错误消息用中文，技术细节（堆栈、内部标识）进日志**

## 9. 数据库映射

- 表/字段 snake_case → 实体 camelCase
- MyBatis-Plus：`@TableName`、`@TableId(type = IdType.AUTO)`、`@TableLogic`、`@TableField(fill = FieldFill.INSERT)`
- 分页统一 `Page<T>`
- 金额用 `BigDecimal`，禁用 `double`

## 10. 数据载体：禁止裸 `List<Map>`

> **这条是硬性拦截。** `List<Map>` / `List<Map<String, Object>>` 作为 Mapper / Service 的返回类型，默认不合格。

### 为什么禁

| 问题 | 后果 |
|---|---|
| 字段名是字符串 | SQL 别名写错、表字段改名，**编译期不报**，运行时才炸或静默返回 null |
| 类型全丢 | 拿到的是 `Object`，每处都要 `(BigDecimal)` 强转，转错就是 `ClassCastException` |
| 无补全无重构 | IDE 无法提示 key，改一个字段得全局搜字符串 |
| 空值陷阱 | 列不存在返回 `null` 而不是报错，排查成本极高 |
| 调用方靠猜 | 下一个接手的人不知道这个 Map 里到底有什么 key |
| 无文档 | 接口契约变成"你自己看 SQL" |

**用 Map 的本质是"不想搞清楚字段"**——和虚构字段名是同一类逃避，只是一个编了假名字，一个干脆不起名字。

### 正确做法

**单表查询 → 返回 Entity：**
```java
public interface OrderMapper extends BaseMapper<Order> {
    List<Order> listByUserId(@Param("userId") Long userId);
}
```

**多表 Join / 只取部分列 → 建 VO（投影对象）：**
```java
// OrderSumVO.java
@Data
public class OrderSumVO {
    private Long orderId;
    private String customerName;
    private BigDecimal totalAmount;
}

// Mapper
List<OrderSumVO> listOrderSum(@Param("batchId") Long batchId);
```
列少也不要紧，3 个字段的 VO 也比 Map 强。VO 就是契约。

**注意**：MyBatis 自动映射要求 `mapUnderscoreToCamelCase=true`（Spring Boot 默认开）。列名 `customer_name` → 字段 `customerName` 自动对上；用别名时保证别名与字段名一致。

### 唯一允许的场景

**列集在编译期无法确定**——典型是动态报表、行列转置、由配置决定输出哪些列。

即便如此也必须满足：

1. 泛型写全：`List<Map<String, Object>>`，**不许裸 `List<Map>`**
2. Mapper 方法上加注释说明**为什么**不能用 VO（"列由报表模板配置决定"）
3. 在 Service 边界内消化掉，**不许泄漏到 Controller 对外响应**
4. 优先考虑替代方案：列集有限且可枚举 → 建宽 VO；列集来自配置 → 用 `LinkedHashMap` 保序并写清 key 契约

### 参数侧同理

- 方法参数超过 3 个、或会被多处传 → 建 DTO，**不用 `Map<String, Object>` 传参**。
- MyBatis 的 `@Param` 多参数是标准做法，不算 Map 传参。
- 动态条件查询用 `QueryWrapper` / `LambdaQueryWrapper`，不拼 Map。

### 自查

```
[ ] Mapper 有没有返回 List<Map> / Map<String,Object>？
    → 有：能不能改成 Entity 或 VO？能就改，不能就按"唯一允许的场景"四条补齐
[ ] Service 方法有没有收 Map 当入参？（超过 3 个键就该建 DTO）
[ ] Controller 有没有把 Map 直接当响应体返回？
[ ] SQL 别名有没有和 VO 字段名对上？mapUnderscoreToCamelCase 开了吗？
```

## 11. 配置

- 配置进 `application.yml`，不硬编码
- 环境分离：`application-dev.yml` / `application-prod.yml`
- 敏感信息走环境变量或配置中心，**不写进代码**

## 12. 常用依赖（按需，别多引）

| 功能 | 依赖 |
|---|---|
| Web | `spring-boot-starter-web` |
| 校验 | `spring-boot-starter-validation` |
| DB | `mybatis-plus-boot-starter` 或 `spring-boot-starter-data-jpa` |
| Redis | `spring-boot-starter-data-redis` |
| 工具 | `lombok`、`hutool-all`（项目已有才用） |
| 测试 | `spring-boot-starter-test` |

## 13. 构建命令

- 有 wrapper 用 wrapper：`./mvnw`
- 编译 `mvn -q compile` / 测试 `mvn -q test` / 打包 `mvn package -DskipTests` / 运行 `mvn spring-boot:run`
- Gradle：`./gradlew compileJava -q` / `./gradlew test`

**改完必须编译。** 只改一个 getter 也要编译。
