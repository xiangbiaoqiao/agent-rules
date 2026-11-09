# 链式 / 函数式风格规范

融合自 Codex `chain-style`，并**已按用户 P0 规则第 4 条收口**（见 `user-rules.md`）。

**用户原话口径：链式适度。`StringBuilder` / `Promise` / `Stream` / `Builder` 适合；单条件 `if` 不硬包链式；禁止为链式牺牲可调试性。**
判定基线：可读性 > 可调试性 > 简洁性 > 风格统一 > 性能微优化。

---

## 1. 该用

| 场景 | 写法 | 注意 |
|---|---|---|
| 集合「过滤 + 映射 + 归约/分组」 | `stream().filter().map().collect()` | 批处理语义最直观 |
| 多级缓存 / 惰性初始化 | `map.computeIfAbsent(key, k -> ...)` | 省掉 get+put 两步 |
| 按条件批量删 | `list.removeIf(pred)` | 一行替掉循环+if+remove |
| 取值带默认 | `map.getOrDefault(k, def)` | value 为 null 也会走默认，需 null 安全用 `Optional.ofNullable` |
| 字符串拼接 | `Collectors.joining()` / `String.join()` | 替掉循环 `+=` |
| 构造多参数对象 | Builder | 参数 > 4 个优先 |
| 可空链式 | `Optional.map().orElse()` | 替掉多层 if-null |

## 2. 禁止

1. **替代单次查找/单元素 if-else**
   `list.stream().filter(x -> x.getId().equals(id)).findFirst()` 不如直接 for 或 Map 查。
2. **链长超过 4–5 个操作符还不拆** → 必须引入中间变量或抽方法。
3. **lambda 里有副作用** → 改外部变量、写库、发 HTTP 出现在 `map`/`filter`/`peek` 里一律禁止。
4. **为省两行引入 stream** → 去掉 stream 后行数增加 ≤ 3 行，就别用。
5. **只被调一次、且无独立业务语义的私有方法** → 内联。（纯技术工具如 `getStringIgnoreCase` 可放 util）
6. **单条件 `if` 硬包成链式** —— 一个 `if` 能说清的分支，不要为了"风格统一"塞进 `Optional`/`Promise` 链。
7. **拿可调试性换链式** —— 链里抛异常定位不到具体环节、断点打不进 `.map()` 的情况，一律退回普通写法。

## 3. 判定（按顺序自问，命中即停）

1. 去掉 stream 后代码行数增加 ≤ 3 行？→ 是：不用。
2. 这段逻辑是否可能被第二处复用？→ 否：不抽方法。
3. 抽出的方法名能否准确描述业务含义？→ 否：内联。
4. 是否在循环体内或高频路径？→ 是：优先普通 `for`，避免装箱/lambda 开销。

全过之后再用链式。

## 4. 不适用（保持简单）

单步赋值取值、循环体短且清晰、需要 `break`/`continue`、性能敏感热路径、需要处理 checked exception。

## 5. 语言适配

| 语言 | 工具 |
|---|---|
| Java | Stream、`Optional`、Builder、`computeIfAbsent`、`removeIf` |
| JS/TS | `map/filter/reduce`、Promise 链、`?.`、`??` |
| Python | 列表推导、生成器表达式、`itertools`、`functools.reduce` |
| C# | LINQ `Where/Select/Aggregate`、`?.` |

## 6. 重构信号

- **传统 → 链式**：多层嵌套 `for` + `if`、手动字符串拼接、多步收集过滤转换。
- **链式 → 传统**：调用链 ≥ 5 层、要处理 checked exception、断点调试难定位。
