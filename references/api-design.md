# 接口设计规范（前后端协作）

> **先读现场。** 本项目的接口有自己的历史风格，下面第 1 节是现状，第 2 节起是新建接口的要求。
> 现有接口不返工（P0 第 10 条），但**新写的接口按本册来**。

---

## 0. 一句话原则

接口是**契约**，不是「我这边能跑就行」。判断标准：前端拿到这个接口，能不能不问你直接对接完。

---

## 1. 现状（照这个来，不要另起炉灶）

| 项 | 项目实际 | 说明 |
|---|---|---|
| 路径前缀 | `/je/<模块名>` | 如 `/je/accountingperiod` |
| 控制器注解 | `@Controller` + `@ResponseBody` | **不是** `@RestController`，跟随现状 |
| 基类 | `extends AbstractPlatformController` | 平台提供了取参、分页等能力，先看它有什么 |
| 返回体 | `BaseRespResult<T>`（`com.je.core.result`） | 平台统一定义，**不要自己造包装类** |
| 前端调用 | `JE.fetch`（`src/app/helper/httpUtil.js`） | 不要新引 axios 实例 |

**新接口的路径命名**：模块内动作式接口沿用平台习惯（`/list`、`/save`、`/delete`），保持同模块一致；全小写、不加分隔符（`accountingperiod`，不要写成 `accounting-period`）。

---

## 2. 返回体：只有一种

`BaseRespResult<T>` 已经是平台标准，字段如下：

| 字段 | 类型 | 含义 |
|---|---|---|
| `code` | String | **成功是 `"1000"`**（不是 200），其余为失败 |
| `message` | String | 面向用户的提示，中文 |
| `errorCode` | String | 业务错误码，供前端分支判断 |
| `obj` | T | 单个对象结果 |
| `rows` | List | 列表结果 |
| `totalCount` | Long | 分页总条数 |
| `exceptionId` | String | 异常追踪 ID，排查时用它查日志 |
| `type` | String | 平台内部标记 |

硬规则：

- **禁止**返回裸 `Map`、裸 `List`、裸 String 当响应体
- **禁止**自己 new 一个 `{"code":200,"data":...}` 的新结构
- 成功用 `BaseRespResult.successResult(...)`，失败用 `BaseRespResult.errorResult(...)`
- 列表 + 分页时，`rows` 放数据、`totalCount` 放总数，**不要把 total 塞进 rows 里**
- **`code` 是字符串 `"1000"`**，前端判断时用 `String(res.code) === '1000'`，不要写 `res.code === 200`

```java
@ResponseBody
@RequestMapping("/list")
public BaseRespResult list(HttpServletRequest request) {
    List<BatchCostVO> voList = batchCostService.listByCondition(query);
    return BaseRespResult.successResult(voList);
}
```

---

## 3. 参数：入参必须有类型

- 入参超过 2 个 → **建 DTO**，不要一长串 `@RequestParam`
- 参数校验用 `@Valid` + JSR-303 注解（`@NotNull` / `@NotBlank` / `@Size`），在 Controller 入口拦住
- **禁止用 `Map<String, Object>` 接参**（P0 第 4 节）

```java
@PostMapping("/save")
@ResponseBody
public BaseRespResult save(@Valid @RequestBody BatchCostDTO batchCostDTO) {
    return BaseRespResult.successResult(batchCostService.save(batchCostDTO));
}
```

---

## 4. HTTP 方法

| 方法 | 用途 | 幂等 | 备注 |
|---|---|---|---|
| GET | 查询 | ✅ | 不产生副作用，不改数据 |
| POST | 新增 / 复杂查询 | ❌ | 重复提交要防（见第 5 节） |
| PUT | 全量更新 | ✅ | 同一请求重复执行结果一致 |
| DELETE | 删除 | ✅ | 逻辑删除也走这里 |
| PATCH | 局部更新 | ⚠️ | 平台用得少，非必要不用 |

- **GET 不写库**：所有 `GET` 接口里出现 `insert`/`update`/`delete` 都算违规
- 查询条件复杂到 URL 装不下（如多选树形条件）用 POST，但要在注释里写明「这是查询接口」

---

## 5. 重复提交与幂等

- 涉及金额、库存、审批提交的接口，**必须有防重**
- 做法：前端提交后禁用按钮 + 后端用业务唯一键（或 `RedisLockUtils`，项目已有）拦一道
- 只靠前端禁用按钮不算数，接口可以被直接调用

---

## 6. 错误处理

- `message` 面向用户，**中文、说人话**；堆栈和技术细节进日志（P0 第 8 条）
- 前端需要区分错误类型时，看 `errorCode`，**不要靠 message 做字符串匹配**
- 同一类错误在整个模块里用同一个 `errorCode`
- 对外**不要**暴露 SQL、表名、类名、堆栈

```java
❌ return BaseRespResult.errorResult("插入 TBATCHCOSTINITBZ 失败: " + e.getMessage());
✅ log.error("批次成本初始化失败, batchId={}", batchId, e);
   return BaseRespResult.errorResult("初始化失败，请稍后重试");
```

---

## 7. 分页、排序、筛选

| 参数 | 约定 |
|---|---|
| 页码 | `pageNumber`（从 1 开始）或项目现有的 `page`，**同一模块内保持一致** |
| 每页条数 | `pageSize`，默认 20，**上限 100**，超过要截断 |
| 排序 | `sortField` + `sortOrder`（`asc`/`desc`），字段名**必须白名单校验**，禁止直接拼进 SQL |
| 筛选 | 放 DTO，不要拼接成 SQL 字符串（P0 第 22 条） |

返回：`rows` = 当前页数据，`totalCount` = 总条数。

---

## 8. 数据格式

| 类型 | 规则 | 原因 |
|---|---|---|
| 时间 | `yyyy-MM-dd HH:mm:ss`；只要日期用 `yyyy-MM-dd` | 前端不用猜格式 |
| 金额 | 后端 `BigDecimal`，**序列化成字符串**返回 | JS number 精度只有 16 位，`0.1+0.2` 会错 |
| 主键 ID | 超过 16 位的 Long 转字符串 | JS 安全整数上限 2^53 |
| 布尔 | 用 `true`/`false`，不要 `0`/`1` | 少一层约定 |
| 枚举 | 返回 `code` + `name` 两个字段 | 前端要显示中文，不想维护映射表 |

---

## 9. 版本与兼容

- **只加字段，不删字段、不改字段含义**——老前端可能还在用
- 字段废弃：先保留并标 `@Deprecated`，确认无调用方后再删
- 破坏性变更（改路径、改结构）→ 新开路径，不要原地改
- 接口返回的 `VO` 不要直接复用作入参 `DTO`

---

## 10. 文件上传下载

- 上传：限制大小和类型，**类型校验不能只看扩展名**，要校验实际内容
- 下载：文件名要 URL 编码，防中文乱码和响应头注入
- 大文件用流式处理，**不要整个读进内存**
- 下载接口不要返回 `BaseRespResult`，直接写 `OutputStream`

---

## 11. 交付前自检

```
[ ] 返回的是 BaseRespResult，不是裸 Map / 裸 List？
[ ] 成功码用的是 "1000"（字符串），前端也按字符串判？
[ ] 入参 >2 个的，建 DTO 了吗？加了 @Valid 吗？
[ ] GET 接口里没有写库操作？
[ ] message 是中文人话，没有把 SQL / 堆栈暴露出去？
[ ] 分页参数 pageSize 有上限校验？排序字段走白名单了？
[ ] 金额是字符串、16 位以上 ID 转字符串了吗？
[ ] 新加的字段是追加的，没有删改老字段？
```
