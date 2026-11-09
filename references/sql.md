# SQL 写作规范

融合自 Codex `sql-helper`。方言细节见同目录 `sql-dialects.md`。

---

## 1. 先确定方言

不确定就问，或从上下文推断（连接串、已有 SQL 写法、文件名）。
**默认按 SQL Server 处理**（本项目主战场：PigData 猪场库 + 润乾报表 ds1）。跨库才翻方言表。

## 2. 六类任务的做法

| 任务 | 做法 |
|---|---|
| **写** | 先说清 schema（表名、字段、关联键）。没 schema 就问，不许猜字段名 |
| **解释** | 按**逻辑执行顺序**讲：`FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`，不按书写顺序 |
| **优化** | 找：缺索引、N+1、隐式类型转换、`SELECT *`、函数包裹索引列、大表无谓排序、`IN` 换 `EXISTS`。给建议时说明预估影响 |
| **方言转换** | 产出目标方言可跑版本，并列出语义差异（分页、字符串拼接、日期函数、标识符引用、布尔、UPSERT、JSON） |
| **排错** | 读错误号 + 消息定位。SQL Server 报错号含义见下节 |
| **建表** | 主键、索引、约束、NULL 语义、类型选择（金额 `DECIMAL(18,4)`，不用 `FLOAT`） |

## 3. 硬规则

1. **必须可执行**，不写伪代码（除非用户只要概念说明）。
2. **显式 `JOIN ... ON`**，禁止逗号隐式连接。
3. 大表关联子查询优先 `EXISTS` 而非 `IN`。
4. 子查询被引用两次以上或嵌套过深 → 抽 `WITH` CTE。
5. 所有表给别名，join 里所有列带别名限定，避免歧义。
6. 关键字大写，一个主句一行，缩进对齐。
7. **参数化。** 任何来自用户的字符串都走参数/变量，禁止拼接。
8. 改数据前：先 `SELECT` 验数 → `BEGIN TRAN` → 改 → 校验 → `COMMIT/ROLLBACK`。批量更新必须给 `WHERE` 并先 `COUNT(*)`。

## 4. SQL Server 踩坑清单（本项目高频）

| 坑 | 现象 | 处理 |
|---|---|---|
| 同层别名自引用 | 在 `UNION ALL` 同一层里引用输出列别名 | 外层包一层 `FROM ( ... ) t` 子查询 |
| 聚合体里混外部引用 + 其它列 | `Msg 8124`「聚合或 GROUP BY 的列同时包含外部引用」 | 段边界从 `SUM(CASE...)` 里挪到 `WHERE`，配 `OUTER APPLY` |
| 列名以数字开头 | `Msg 102 '.' 附近有语法错误` | 限定名加方括号：`t.[5周死淘率]` |
| `NULL` 参与运算 | 整行结果变 `NULL` | `ISNULL(x,0)` / `COALESCE` |
| 隐式类型转换 | 索引失效、全表扫 | 比较两侧类型一致（`varchar` vs `nvarchar` 也会） |
| `COUNT(*)` vs `COUNT(col)` | 计数不一致 | `COUNT(col)` 不数 NULL |
| 除零 | `Msg 8134` | `NULLIF(分母,0)` |
| 报表表达式里的 `-` | 润乾把字段名里的 `-` 当减号 | 字段别名用下划线：`校正7_125kg料肉比` |

## 5. 报表场景（润乾 ds1）

- 报表 SQL 的**输出列名 = 报表绑定的字段名**，改名字会让报表整列变空。改列名前先跑 `raqsoft-rpx-reader` 的 `cells` 确认绑定。
- 输出列顺序尽量少动；必须动就在末尾追加。
- 大 SQL 改动前先备份原文件，并留一份 `md5`。
- 交付前跑一次测试库，`rc=0` + 0 错误 + 列数/行数对得上。

## 6. 优化检查表

```
[ ] 有没有 SELECT *（大表/宽表必查）
[ ] WHERE 里的列有没有被函数包裹（DATEADD(col,...) / CAST(col...) 会让索引失效）
[ ] 关联键两侧类型是否一致
[ ] 大表关联是否走了索引（看执行计划：Table Scan / Index Scan 报警）
[ ] 是否在 SQL 里做本该在应用层做的循环
[ ] 排序是否必要（无 ORDER BY 需求就别加）
[ ] 是否有 N+1（循环里查库）
[ ] CTE 是否被多次引用（只引一次就没必要抽）
```

## 7. 格式样例

```sql
WITH Base AS (
    SELECT a.BATCH_ID,
           a.FARM_ID,
           SUM(ISNULL(c.AMT, 0)) AS AMT_SUM
      FROM TBATCH a
      LEFT JOIN TCOST c
             ON c.BATCH_ID = a.BATCH_ID
     WHERE a.STATUS = 1
     GROUP BY a.BATCH_ID, a.FARM_ID
)
SELECT b.BATCH_ID,
       b.FARM_ID,
       b.AMT_SUM,
       ISNULL(d.NAME, '') AS FARM_NAME
  FROM Base b
  LEFT JOIN TFARM d
         ON d.ID = b.FARM_ID
 ORDER BY b.BATCH_ID;
```
