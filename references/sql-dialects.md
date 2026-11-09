# SQL Dialect Differences Reference

Quick-reference for cross-dialect SQL conversion. Covers the most common divergence points.

## Pagination

| Dialect | Syntax |
|---------|--------|
| MySQL / PostgreSQL / SQLite | SELECT ... LIMIT n OFFSET m |
| SQL Server (2012+) | SELECT ... ORDER BY col OFFSET m ROWS FETCH NEXT n ROWS ONLY |
| SQL Server (legacy) | SELECT TOP n ... (no standard offset) |
| Oracle (12c+) | SELECT ... FETCH FIRST n ROWS ONLY (offset via OFFSET m ROWS) |
| Oracle (legacy) | WHERE ROWNUM <= n (with subquery for offset) |

## String Functions

| Operation | MySQL | PostgreSQL | SQL Server | Oracle | SQLite |
|-----------|-------|------------|------------|--------|--------|
| Concat | CONCAT(a,b) or a,b with \|\| in ANSI mode | a \|\| b | a + b or CONCAT(a,b) | a \|\| b | a \|\| b |
| Length | LENGTH() or CHAR_LENGTH() | LENGTH() or CHAR_LENGTH() | LEN() (excludes trailing spaces) or DATALENGTH() | LENGTH() | LENGTH() |
| Substring | SUBSTR() or SUBSTRING() | SUBSTR() or SUBSTRING() | SUBSTRING() | SUBSTR() | SUBSTR() |
| Find position | LOCATE(sub,str) or INSTR() | POSITION(sub IN str) or STRPOS() | CHARINDEX(sub,str) | INSTR(str,sub) | INSTR(str,sub) |
| Replace | REPLACE() | REPLACE() | REPLACE() | REPLACE() | REPLACE() |
| Trim | TRIM() / LTRIM() / RTRIM() | TRIM() / LTRIM() / RTRIM() | TRIM() / LTRIM() / RTRIM() | TRIM() / LTRIM() / RTRIM() | TRIM() / LTRIM() / RTRIM() |
| Upper/Lower | UPPER() / LOWER() | UPPER() / LOWER() | UPPER() / LOWER() | UPPER() / LOWER() | UPPER() / LOWER() |

## Date/Time Functions

| Operation | MySQL | PostgreSQL | SQL Server | Oracle | SQLite |
|-----------|-------|------------|------------|--------|--------|
| Current timestamp | NOW() or CURRENT_TIMESTAMP | NOW() or CURRENT_TIMESTAMP | GETDATE() or SYSDATETIME() | SYSDATE or CURRENT_TIMESTAMP | DATETIME('now') |
| Current date | CURDATE() or CURRENT_DATE | CURRENT_DATE | CAST(GETDATE() AS DATE) or CONVERT(date,GETDATE()) | TRUNC(SYSDATE) or CURRENT_DATE | DATE('now') |
| Add days | DATE_ADD(d, INTERVAL n DAY) or d + INTERVAL n DAY | d + INTERVAL 'n days' or d + n | DATEADD(day, n, d) | d + n (days) or d + NUMTODSINTERVAL(n,'DAY') | DATE(d, '+n days') |
| Add months | DATE_ADD(d, INTERVAL n MONTH) | d + INTERVAL 'n months' | DATEADD(month, n, d) | ADD_MONTHS(d, n) | DATE(d, '+n months') |
| Date diff (days) | DATEDIFF(day, d1, d2) or d2-d1 | d2 - d1 (returns integer) | DATEDIFF(day, d1, d2) | d2 - d1 (returns number) | JULIANDAY(d2) - JULIANDAY(d1) |
| Extract year | YEAR(d) or EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | YEAR(d) or DATEPART(year, d) | EXTRACT(YEAR FROM d) | STRFTIME('%Y', d) |
| Format date | DATE_FORMAT(d, fmt) | TO_CHAR(d, fmt) | FORMAT(d, fmt) or CONVERT(varchar, d, style) | TO_CHAR(d, fmt) | STRFTIME(fmt, d) |

## Type Casting

| Dialect | Syntax |
|---------|--------|
| MySQL | CAST(x AS type) or CONVERT(x, type) |
| PostgreSQL | x::type or CAST(x AS type) |
| SQL Server | CAST(x AS type) or CONVERT(type, x) |
| Oracle | CAST(x AS type) or TO_CHAR/TO_NUMBER/TO_DATE |
| SQLite | CAST(x AS type) (limited type affinity) |

## NULL Handling

| Operation | MySQL | PostgreSQL | SQL Server | Oracle | SQLite |
|-----------|-------|------------|------------|--------|--------|
| Coalesce | COALESCE(a,b,...) | COALESCE(a,b,...) | COALESCE(a,b,...) | NVL(a,b) or COALESCE(a,b,...) | COALESCE(a,b,...) |
| Null-if-equal | NULLIF(a,b) | NULLIF(a,b) | NULLIF(a,b) | NULLIF(a,b) | NULLIF(a,b) |
| IFNULL equivalent | IFNULL(a,b) | COALESCE(a,b) | ISNULL(a,b) | NVL(a,b) | IFNULL(a,b) |

## UPSERT (Insert or Update)

| Dialect | Syntax |
|---------|--------|
| MySQL | INSERT INTO t (...) VALUES (...) ON DUPLICATE KEY UPDATE col=val |
| PostgreSQL | INSERT INTO t (...) VALUES (...) ON CONFLICT (key) DO UPDATE SET col=EXCLUDED.col |
| SQL Server | MERGE INTO t USING src ON (condition) WHEN MATCHED THEN UPDATE SET ... WHEN NOT MATCHED THEN INSERT ... |
| Oracle | MERGE INTO t USING src ON (condition) WHEN MATCHED THEN UPDATE SET ... WHEN NOT MATCHED THEN INSERT ... |
| SQLite | INSERT INTO t (...) VALUES (...) ON CONFLICT (key) DO UPDATE SET col=excluded.col |

## Window Functions

All major dialects support standard window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, SUM() OVER, etc.) with the same syntax:

`sql
function() OVER (PARTITION BY col ORDER BY col ROWS BETWEEN n PRECEDING AND n FOLLOWING)
`

Differences:
- Oracle supports ROWS BETWEEN and RANGE BETWEEN with full ANSI syntax.
- SQL Server supports ROWS and RANGE but not GROUPS (pre-2022).
- MySQL 8.0+ supports full window function syntax.
- PostgreSQL has full support including GROUPS (11+).

## Boolean and Conditional

| Operation | MySQL | PostgreSQL | SQL Server | Oracle | SQLite |
|-----------|-------|------------|------------|--------|--------|
| Boolean literal | TRUE/FALSE (stored as 1/0) | TRUE/FALSE (native boolean) | 1/0 (BIT) | 1/0 or 'Y'/'N' | 1/0 |
| Conditional | IF(cond,a,b) or CASE WHEN | CASE WHEN | CASE WHEN or IIF(cond,a,b) (2012+) | CASE WHEN or DECODE(cond,a,b) | CASE WHEN |
| DECODE equivalent | CASE WHEN or IF() | CASE WHEN | CASE WHEN | DECODE(expr,val1,res1,...) | CASE WHEN |

## Identifier Quoting

| Dialect | Quote Character | Example |
|---------|----------------|---------|
| MySQL | Backtick | \	able_name\ |
| PostgreSQL | Double quote | "table_name" |
| SQL Server | Square brackets | [table_name] |
| Oracle | Double quote | "table_name" |
| SQLite | Double quote or backtick | "table_name" or \	able_name\ |

## JSON Support

| Dialect | JSON Type | Key Operators |
|---------|-----------|---------------|
| MySQL | JSON | -> and ->> operators (8.0+), JSON_EXTRACT() |
| PostgreSQL | JSONB (preferred) / JSON | -> (object), ->> (text), #> (path), @> (contains) |
| SQL Server | NVARCHAR with IS JSON check | JSON_VALUE(), JSON_QUERY(), OPENJSON() |
| Oracle | CLOB or JSON type (21c+) | JSON_VALUE(), JSON_QUERY(), JSON_TABLE() |
| SQLite | TEXT (no native type) | -> and ->> operators (3.38+), JSON_EXTRACT() |

## Common Gotchas

1. **Implicit type conversion**: MySQL and SQLite are very permissive; PostgreSQL and Oracle are strict. A query that works in MySQL may fail in PostgreSQL due to type mismatches.
2. **GROUP BY strictness**: PostgreSQL requires all non-aggregated SELECT columns in GROUP BY. MySQL (with ONLY_FULL_GROUP_BY disabled) and SQLite allow omitting them.
3. **String comparison**: MySQL is case-insensitive by default (depends on collation). PostgreSQL is case-sensitive. SQL Server is case-insensitive by default (depends on collation).
4. **Empty string vs NULL**: Oracle treats empty string '' as NULL. Other dialects distinguish them.
5. **AUTO_INCREMENT syntax**: MySQL uses AUTO_INCREMENT; PostgreSQL uses SERIAL or GENERATED ALWAYS AS IDENTITY; SQL Server uses IDENTITY; Oracle uses GENERATED ALWAYS AS IDENTITY (12c+) or sequences; SQLite uses AUTOINCREMENT.
