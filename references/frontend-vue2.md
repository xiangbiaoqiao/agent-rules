# 前端规范（Vue 2 存量项目）

> **先读第一节。** 这是一个 Vue 2 存量项目，本册的基调是「稳定维护」，不是「教你怎么写好 Vue」。
> 下面的规则默认服从项目现状；与项目实际冲突时，以项目为准（P1）。

---

## 0. 前提：Vue 2 已经 EOL

Vue 2 于 **2023-12-31 正式终止支持**（最终版本 2.7.16），官方不再发布新功能、bug 修复和安全补丁。

所以本册的立场是：

| 场景 | 做法 |
|---|---|
| 修 bug、改文案、加小功能 | 正常改，按本册写 |
| 大改页面、新增复杂模块 | 先评估能否用 Vue 3 新开；必须留在 Vue 2 时按本册写 |
| 「顺手升级 Vue / Element UI」 | **不做**。升级是独立任务，要单独评估回归面 |
| 引入新依赖（新 UI 库、新状态库、新工具） | **默认拒绝**，除非说明为什么现有依赖解决不了 |

Vue 2 的老代码不返工（P0 第 10 条）。本册只约束**你新写或正在改**的那部分。

---

## 1. 先读现场：这个项目的实际技术栈

不要凭「Vue 最佳实践」直接开写。项目现状是：

| 项 | 实际值 | 含义 |
|---|---|---|
| Vue | `2.6.10` | Options API 为主，支持但未采用 Composition API |
| UI 库 | Element UI `2.15.13` | 表单/表格/弹窗一律用它，不要混别的 UI 库 |
| 请求 | 平台封装 `JE.fetch`（`src/app/helper/httpUtil.js`） | **不要新引 axios 实例** |
| 状态管理 | **没有 Vuex**（287 个组件里 0 个使用） | 不要为了"规范"引入 Vuex，也不要把现有 props 改成 store |
| 工具库 | lodash / moment / dayjs / echarts 4.9 | 日期优先用 dayjs（moment 只在既有代码里沿用） |
| 目录 | `src/pc/vue/modules/<业务模块>/` | 模块内自带 `api/`、`components/` |

**请求写法**：跟着同模块现有代码走。模块里有 `api/xxx.js` 就在那里加方法，不要直接在组件里拼 URL。

---

## 2. 组件规模（本册最要紧的一条）

项目里已经存在几个巨无霸：

```
liChaVideo.vue            4031 行
liChaDataViewNew.vue      3946 行
baojinDataView.vue        3497 行
```

这三个是**反面教材**，不要照着学。

- **新组件硬上限：300 行**（含 template + script + style）
- 超了按「区块」拆：查询表单、数据表格、编辑弹窗、图表卡片各是一个组件
- 拆出来的子组件放同目录 `components/` 下
- 老组件不主动返工，但**如果你的改动让它变更长，先拆再加**

判据：打开文件要滚动超过 3 屏才能看完 `script`，就该拆了。

---

## 3. 命名

| 对象 | 规则 | 例 |
|---|---|---|
| 组件文件 | PascalCase | `BatchCostDialog.vue` |
| 组件 `name` | 与文件名一致 | `name: 'BatchCostDialog'` |
| 方法 | 动词开头 | `loadList` / `handleSubmit` / `resetQuery` |
| 布尔 props | `is` / `has` / `show` 前缀 | `isDisabled` / `showFooter` |
| 事件 | kebab-case | `@row-click` / `@size-change` |
| 常量 | `UPPER_SNAKE_CASE` + `const` | `const MAX_PAGE_SIZE = 100` |

- 变量命名沿用 P0 第 6 条：数组/列表带 `List` 后缀（`rowList`、`idArr`），映射带 `Map`
- 禁止 `a`、`b`、`obj`、`data`、`item`、`res` 这类泛化名（P0 第 11 条）
- 接口返回的变量按业务语义命名：`const batchCostList = res.data`

---

## 4. 组件契约

```vue
props: {
  visible: { type: Boolean, default: false, required: true },
  batchId: { type: [String, Number], default: null },
  rowList: { type: Array, default: () => [] }   // 对象/数组的 default 必须用工厂函数
}
```

- **props 三件套写全**：`type` + `default` + 必填时 `required`
- **禁止直接改 props**：`this.batchId = x` 一律不合格，改用 `this.$emit('update:batchId', x)`
- `v-model` 用 `value` + `input`（Vue 2 约定，别用 `modelValue`）
- `$emit` 事件名不带 `on` 前缀，用动词或名词：`submit` / `change` / `close`
- 向父组件传多个值时，优先传对象（`{ id, name }`），不要一次 emit 五六个参数

---

## 5. 模板陷阱（踩得最多的一类）

```vue
<!-- ✅ key 用业务主键 -->
<tr v-for="item in rowList" :key="item.batchId">

<!-- ❌ 用 index 当 key：删除/排序后组件状态错位 -->
<tr v-for="(item, index) in rowList" :key="index">
```

- **`v-for` 必须带 `:key`**，且优先用业务主键；只有纯静态列表才允许 index
- **`v-if` 和 `v-for` 不要写在同一个元素上**：Vue 2 里 `v-for` 优先级更高，`v-if` 拿不到循环变量。需要筛选时先用 computed 过滤
- **模板里不要调用方法**：`{{ formatDate(item.time) }}` 每次重渲染都会执行，改用 computed 或提前处理好数据
- `v-html` 只用于**可信内容**（见 `security-general.md`），用户输入一律不用

---

## 6. 响应式与数据

Vue 2 的响应式有硬限制，绕不过去：

```js
// ✅ 新增属性
this.$set(this.form, 'newField', value);

// ❌ 直接赋值：不是响应式的，视图不更新
this.form.newField = value;

// ✅ 改数组元素
this.$set(this.rowList, index, newRow);
this.rowList.splice(index, 1, newRow);

// ❌ 索引赋值不触发更新
this.rowList[index] = newRow;
```

- **只读字典/配置**用 `Object.freeze()` 包一层，跳过响应式转换，大对象能明显省内存
- `computed` 里不要有副作用（不要发请求、不要改 state）——需要副作用用 `watch`
- `watch` 深度监听大对象代价高，尽量监听具体字段

---

## 7. 性能与内存泄漏

**这一节是重点，项目里最容易出的线上问题是内存泄漏。**

```js
mounted() {
  this.timer = setInterval(this.refresh, 30000);
  window.addEventListener('resize', this.handleResize);
}

beforeDestroy() {          // 必须清理
  clearInterval(this.timer);
  window.removeEventListener('resize', this.handleResize);
  if (this.chart) {
    this.chart.dispose();  // echarts 必须 dispose，否则 canvas 泄漏
  }
}
```

必查清单：

- [ ] `setInterval` / `setTimeout` 有没有在 `beforeDestroy` 清掉
- [ ] `window.addEventListener` / `document.addEventListener` 有没有移除
- [ ] echarts 实例有没有 `dispose()`；**不要每次刷新都 `init`**，复用实例调 `setOption({ ... }, true)`
- [ ] `EventBus.$on` 有没有对应的 `$off`
- [ ] 表格一次渲染几万行 → 必须分页或虚拟滚动

其他：

- 大列表分页，单页默认 20~50 条，上限 100
- 图片走懒加载，首屏外的不要一次性加载
- 避免在 `updated` 里改数据（会死循环）

---

## 8. 与后端接口

详见 `api-design.md`，这里只讲前端侧：

- **统一在请求拦截器里判错误码**，组件里不要每个请求都写 `if (res.code !== 200)`
- 组件里只处理「业务失败的具体提示」，通用错误（登录失效、系统异常）交给拦截器
- loading 状态：按钮提交时禁用 + 加载态，不要让用户能连点两次
- 请求失败要有用户可见的提示，禁止静默失败

---

## 9. 改哪个目录（最容易踩的一条）

| 路径 | 性质 | 能不能改 |
|---|---|---|
| `pigdata-frontend/.../src/**` | **源码** | ✅ 只改这里 |
| `je-web/src/main/webapp/pro/`、`static/`、`plugin/` | 构建产物 | ❌ 改了会被覆盖 |
| `je-web/src/main/webapp/*.jsp` | 源码（JSP 页面） | ✅ 可以直接改 |
| `je-web/src/main/webapp/static/js/je-*.js` | 手写 JS（非构建产物） | ✅ 可以改 |

判据：**这个文件在 `pigdata-frontend/src` 里有对应源文件吗？** 有 → 改源文件；没有且是手写的 → 可以直接改产物目录里的那个文件。

---

## 10. 交付前自检

```
[ ] 新组件 ≤ 300 行？超了拆了吗？
[ ] v-for 都有 :key，且不是 index？
[ ] v-if 和 v-for 没写在同一个元素上？
[ ] props 三件套写全了？有没有直接改 props？
[ ] 定时器/监听/echarts 在 beforeDestroy 里清理了吗？
[ ] 改动在 src 里，没有直接改构建产物？
[ ] 起服务实际点一遍了吗？（没点过不许说完成）
```
