# X-HD Paper App 对 RTDL 语言与系统的考核、影响和改进报告

日期：2026-07-10
状态：X-HD 当前范围已完成并通过外部评审
最终状态：`xhd_same_input_directed_hdresult_reproduction_complete__externally_reviewed_and_approved`

## 1. 执行摘要

X-HD paper reproduction app 对 RTDL 的价值，不是为系统增加一个名为
`XHD` 或 `Hausdorff` 的专用内核，而是用一个真实的大规模空间算法检验
RTDL 是否能够：

1. 用通用数据流原语表达 directed Hausdorff distance；
2. 在数十万到数千万点的输入上执行不规则 nearest-neighbor 搜索；
3. 在 OptiX、Numba、Triton 和 NumPy 等执行层之间维持清晰契约；
4. 正确区分标量结果、逐源 witness、运行时状态和性能分母；
5. 把论文压力沉淀为有非论文消费者的通用系统 API；
6. 在探索滑向作者内部 artifact 反向工程时及时止损。

最终证明：

```text
给定相同输入文件：
author C++/CUDA/OptiX hd_exec
与
RTDL/Python/partner route
在 7 个主案例上得到相同的 directed input1-to-input2 HDResult，
全部位于声明容差内。
```

同时，RTDL core 没有新增 X-HD 专用 primitive。Hausdorff 仍然是 app 对
通用 nearest、witness、max-nearest、cell-MBR 和 frontier 能力的组合。

因此，本项目对 RTDL 的最重要结论是：

> RTDL 已经能够把大规模 directed Hausdorff 表达为通用空间数据流，并以
> 多种后端执行；论文 app 验证的是语言组合能力，而不是核心中的论文特供。

## 2. X-HD 为什么是有价值的系统考卷

Directed Hausdorff distance 定义为：

```text
H(A, B) = max over a in A of min over b in B of distance(a, b)
```

在语言层可以拆成：

```text
A x B distance candidates
-> group by source point
-> nearest target witness per source
-> global maximum over nearest distances
```

这个定义看似简单，但它同时包含四类系统压力：

- 大规模候选空间，不能物化完整笛卡尔积；
- 每个 source point 的不规则 nearest 搜索；
- 局部 argmin 与全局 argmax 的组合规约；
- witness、标量结果、提前终止和并行 tie-break 的精确语义。

在代表性 3-D 输入中，规模包括：

```text
Dragon -> HappyBuddha:
437,645 x 543,652

ThaiStatuette-scaled -> HappyBuddha:
4,999,996 x 543,652

ThaiStatuette-scaled -> AsianDragon-scaled:
4,999,996 x 3,609,600
```

Geo 路线还覆盖：

```text
WaterBodies -> BlockGroups full-public:
22,824,823 x 52,271,467
```

这使 X-HD 成为比 tiny benchmark 更严格的语言考核：任何依赖 Python
逐行对象、完整 pair materialization 或全数组排序的设计都会迅速暴露。

## 3. 对语言表达能力的考核

### 3.1 Hausdorff 是否必须成为核心 primitive

答案是否定的。

RTDL 最终把 Hausdorff 保持为 app 组合：

```text
pairwise_l2_distance_candidate_rows_numpy_columns
-> nearest_witness_numpy_columns
-> max_nearest_distance_witness_numpy_columns
```

兼容 wrapper：

```text
directed_hausdorff_2d_numpy_columns
directed_hausdorff_3d_numpy_columns
```

这些 wrapper 调用上述通用 helper，而不是实现另一份 X-HD 专用逻辑。

这项设计的意义是：

- 语言暴露的是数据关系和规约；
- app 决定这些规约在当前领域中叫 Hausdorff；
- backend 可以替换候选生成或 nearest 执行，而不改变 app 语义；
- 系统不需要知道论文名称、Figure 编号或作者内部状态机。

### 3.2 通用性是否只是命名上的

不是。

Goal5128 增加了独立的非 Hausdorff 消费者：

```text
facility service radius
worst-served demand
```

它直接复用相同的 nearest/max-nearest 管线，不调用
`directed_hausdorff_*` wrapper。

这证明：

```text
nearest witness + max nearest
```

是通用设施选址、覆盖半径和最差服务距离能力，不是给 X-HD 换了一个中性名字。

## 4. 对正确性模型的考核

### 4.1 Directed 与 symmetric 必须行为可区分

早期仅在对称输入上得到相同数字，不能证明实现了作者的 directed 语义。

项目随后加入判别性 fixture：

```text
directed A -> B = 0.5
directed B -> A = 9.0
symmetric Hausdorff = 9.0
author HDResult = 0.5
RTDL HDResult = 0.5
```

这个 fixture 能证伪错误实现：如果 RTDL 或 comparator 偷偷计算 symmetric
Hausdorff，就会得到 `9.0` 并失败。

它确立了正式合同：

```text
HDResult = directed input1 -> input2
```

### 4.2 标量精确与 witness 精确是两个合同

X-HD 揭示了一个重要语言问题：

```text
最终 max-nearest 标量正确
不等于
每个 source point 的 nearest witness 都被精确计算
```

`cell-mbr-fast-scalar` 使用全局 bound early-break。只要某个 source 已无法
改变最终最大值，它可以提前结束。这样能保持最终 HDResult 精确，但大量逐源
witness 可能只是上界状态。

因此系统显式记录：

```text
per_source_witness_exact = false
```

`cell-mbr-exact-witness` 则保留：

```text
per_source_witness_exact = true
```

Goal5451 的 7 个主案例全部采用 exact-witness 证据。3 个 fast-scalar 结果只
作为附加 scalar-only 证据。

这项改进超出 X-HD 本身：任何允许短路、近似状态或目标导向规约的数据流语言，
都必须把“最终答案精确”和“中间 witness 精确”分别建模。

### 4.3 容差必须按数值合同声明

不同路径可能使用 author float32、RTDL float64 或不同 partner 的计算顺序。
项目没有要求不合理的 bitwise equality，而是逐案声明容差：

- graphics：`1e-6`；
- bounded geo：`1e-5`；
- full-public WaterBodies/BlockGroups：`2e-6`。

最后一个案例的差值约 `1.31e-6`，是最紧余量。其 `2e-6` 边界来自
Goal5314 已记录的 author float32 与 RTDL float64 exact-witness 比较，不是
Goal5451 看到结果后临时选择。

## 5. 沉淀到 RTDL 的正式系统能力

### 5.1 通用列式 nearest pipeline

正式导出的基础能力包括：

| 能力 | 系统作用 | X-HD 中的用途 |
|---|---|---|
| `pairwise_l2_distance_candidate_rows_numpy_columns` | 生成带 source/target id 的 L2 候选列 | bounded/reference 路线 |
| `nearest_witness_numpy_columns` | 每个 source 的稳定 argmin | 每点最近 target |
| `max_nearest_distance_witness_numpy_columns` | 对 nearest rows 做 max 与稳定 tie-break | directed HDResult |
| `directed_hausdorff_2d_numpy_columns` | 通用 helper 的 2-D 组合 wrapper | 2-D app front door |
| `directed_hausdorff_3d_numpy_columns` | 通用 helper 的 3-D 组合 wrapper | 3-D app front door |

核心变化是从“系统提供 Hausdorff 算法”转向“系统提供可组合的关系和规约”。

### 5.2 通用空间索引与 frontier API

大规模路线不能生成所有 pair rows，因此项目继续抽取：

```text
grid/cell descriptors
cell-MBR candidate generation
nearest-state seed
frontier split
cell-MBR traversal row-table ABI
native 3-D AABB / cell-MBR front door
inline nearest payload execution
frontier capacity retry
```

代表性公开 API 包括：

```text
seed_nearest_witness_from_local_grid_cell_numpy_columns
cell_mbr_nearest_frontier_numpy_columns
```

这批能力不是 Hausdorff 专属。它们表达的是：

> 给定 query points、target points、空间 cell MBR 和当前 nearest state，
> 生成需要继续处理、可以 inline 处理或可以剪枝的通用 frontier。

这可以被其他 kNN、覆盖、最远最近点、空间过滤和迭代查询使用。

### 5.3 通用 worklist 与状态表达

X-HD 的 heavy-cell/offload 压力推动了：

```text
heavy_offload_worklist_numpy_columns
active/miss/deferred row schema
queue/peak telemetry
active-query status reference
```

这部分提供了通用工作队列和状态表达，但必须诚实评价：

- 通用 schema 与非 X-HD 消费者是有效资产；
- 对齐作者 `-lb` 行、hash、namespace 和内部 status stream 的大量后续探索
  没有形成等比例系统价值；
- 这些方向最终由 Stop-Loss Gate 关闭，不能再当作论文复现进度。

## 6. 执行系统的具体改进

### 6.1 减少 Python 行对象和重复打包

X-HD 的大输入首先暴露了 front-door 成本。

改进包括：

- 输入直接加载为 NumPy coordinate matrix；
- seed/frontier 复用 packed coordinate matrix；
- 保留旧 row helper 供 bounded/reference 路线使用；
- app-owned ASCII PLY loader 使用列式读取而不是逐行 tuple 构造；
- all-source 路线使用 no-copy view，不再物化 subset。

效果：

```text
source + target column construction:
约 0.535s -> 约 0.001-0.002s

full input loading:
约 2.52s -> 约 0.68s
```

这证明 columnar front door 对 Python 语言系统是必要基础设施，而不是微优化。

### 6.2 更高效的 seed

最初 nearest-cell-MBR seed 对每个 query 扫描大量 cell MBR：

```text
query_count = 437,645
nonempty_cell_count = 6,454
cell_mbr_tests ≈ 2.82B
seed ≈ 4.04s
```

项目加入 generic local-grid seed，并把 occupied-cell lookup 从反复二分搜索改为
dense encoded-cell lookup，保留大 grid fallback。

seed 最终降至约 `0.22s` 量级。

### 6.3 payload current-best 剪枝

native inline-nearest 最初进行了约 `1.24B` point-distance evaluations。

关键修复：

1. any-hit 使用不断更新的 payload current-best；
2. intersection 在 `optixReportIntersection` 前检查 cell MBR 是否已被当前
   best 排除；
3. intersection 计算的 `min_sq` 通过 attribute 传给 any-hit；
4. 只有真正输出 row 时才计算 row-only 距离字段。

效果：

```text
inline point evaluations:
约 1.24B -> 约 0.40B

native frontier/inline 阶段：
降至约 0.93-0.94s（中间阶段证据）
```

这些优化属于通用 nearest traversal，不包含 X-HD app 身份。

### 6.4 max-nearest 规约从全排序变为线性

原实现为了稳定 tie-break 对全部 nearest rows 做 lexsort。

改进后：

```text
finite maximum
-> 只提取 maximum tie set
-> 仅对 tie set 做稳定排序
```

效果：

```text
max-nearest reduction:
约 0.072s -> 约 0.0007-0.0008s
```

这是标准的通用规约优化，适用于 max/min witness 类查询。

### 6.5 后端和 partner 边界

X-HD 同时使用或验证了：

- OptiX：native cell-MBR / inline nearest；
- Numba：CPU/CUDA partner 与 seed/reference 路线；
- Triton：2-D dense tiled max-of-nearest；
- NumPy：reference、front door 和稳定 comparator。

项目暴露了一个未完全解决的系统问题：partner/backend 工具链兼容性还不统一。
例如某 POD 上 Numba 生成 PTX 8.7，而可用路径只接受 PTX 8.4，2-D geo 路线转而
使用 Triton。

因此未来 RTDL 需要把 backend capability、PTX compatibility 和 fallback
选择做成显式系统能力，而不是由 paper app 临时判断。

## 7. RTDL 自身性能演化

以下数字只用于描述 RTDL 同一代表 workload 的自身演化，不是 author speedup：

| 阶段 | 代表 route wall | 主要变化 |
|---|---:|---|
| Goal5188 初始 full-public route | 约 7.30s | 初始 cell-MBR / continuation 路线 |
| Goal5189 | 约 5.98s | local-grid seed |
| Goal5191 | 约 3.65s | inline-nearest 512，frontier rows 归零 |
| Goal5195 | 约 2.6s | intersection-stage current-best prune |
| Goal5196 | 约 2.26s | dense local-grid lookup |
| Goal5202 | 约 2.03s | packed coordinate matrix 复用 |
| Goal5203 | 约 1.24s | NumPy matrix input front door |
| Goal5204/5205 | 约 1.17s | 线性 max-nearest 与快速 PLY loader |
| Goal5217 fresh scalar median | 约 0.840s | global-bound early-break 等最终路线 |
| Goal5217 explicit-warm median | 约 0.290s | warmup 单列，诊断口径 |

按最终 scalar HDResult 合同计算：

```text
route: 7.30s -> 0.84s，约 8.7x RTDL 内部改善
full total: 10.01s -> 1.52s，约 6.6x RTDL 内部改善
```

这两个倍数只能描述 RTDL 自身版本演化。最终 scalar 路线的
`per_source_witness_exact=false`，所以不能把它和 exact-witness 路线混为同一
输出合同。

Goal5451 的重复性能附录为：

```text
author internal Running.AvgTime median = 7.722ms
author process wall median             = 1.9058s
RTDL fresh route median                = 0.8396s
RTDL fresh total median                = 1.5200s
RTDL explicit-warm route median        = 0.2896s
RTDL load + warmup + measured median   = 1.8121s
```

不报告 author-vs-RTDL ratio，原因不是硬件不同。Goal5217 是同一 POD、同一输入。
真正原因是：

- author internal time 与 process wall 不同；
- RTDL route 与含加载 total 不同；
- warm route 排除了单列 warmup；
- author 与 RTDL 算法和输出合同不同。

## 8. 7 个最终主案例证明了什么

最终主矩阵：

| 类别 | 案例数 | 输入身份 | Witness | 结果 |
|---|---:|---|---|---|
| Directed 定义判别 | 1 | checked-in bounded fixture | exact | matched |
| 3-D graphics | 3 | Level-B same-source public | exact | matched |
| 2-D bounded geo | 2 | Level-B bounded fixture | exact | matched |
| 2-D full-public geo | 1 | Level-B full-public same-source，非 exact paper hash | exact | matched |

合计：

```text
primary cases = 7
matched = 7
exact witness = 7
additional fast-scalar routes = 3 / 3 matched
```

它证明的是跨实现的 same-input functional equivalence：

```text
same input files
-> same directed HDResult within tolerance
```

它不证明：

- 使用了论文原始字节完全相同的数据集；
- 复现 Figure 5/7/8/9/10/11；
- RTDL 与作者内部 RT-core 算法相同；
- worklist、`-lb`、row hash 或内部状态流相同；
- RTDL 相对作者有性能 parity 或 speedup。

## 9. App 与系统的所有权边界

### 9.1 继续属于 X-HD app

```text
author hd_exec 构建兼容补丁与运行 wrapper
paper/source input acquisition
PLY/WKT/OFF 解析选择与 app preprocessing
same-input comparator
逐 workload tolerance
author-compatible JSON 输出
paper log 和 Figure 映射
性能 regime 选择与 claim boundary
```

这些内容不能提升为 RTDL 核心语义。

### 9.2 属于 RTDL 系统

```text
generic point columns
pairwise L2 rows
nearest witness
max-nearest reducer
grid/cell descriptors
nearest-state frontier
cell-MBR traversal ABI
native inline nearest
frontier retry/capacity
generic worklist/status rows
partner capability and columnar contracts
```

系统能力必须满足：

- app-neutral 命名；
- 无 paper/author/Figure identity；
- 至少一个非 X-HD 消费者或行为测试；
- 清楚的 exact/approximate contract；
- backend 缺失时 fail-closed 或显式 fallback。

## 10. 走过的弯路和止损

项目曾在 exact paper artifact 不可得后，继续投入大量目标追逐：

```text
author -lb rows
row identity
hash parity
status stream
cell namespace reconciliation
full-cover internal artifacts
```

这些工作的问题是：

- 成功往往需要编码作者 app 专属状态；
- 唯一下游 Figure 复现被缺失数据阻断；
- 多个目标没有产生新的非 X-HD 消费者；
- 进展被“更接近内部 artifact”替代，而不是“新增通用语言能力”。

因此项目引入并执行 Stop-Loss Gate：

```text
gate_generic_capability_produced
gate_non_app_consumer
gate_requires_app_specific_logic
gate_downstream_consumer_reachable
```

当前结论：

```text
do not reopen author artifact parity
```

这是 X-HD 对研发治理的另一项系统改进：paper app 不仅要验证代码，也要限制
反向工程无底洞。

## 11. 暴露出的剩余 RTDL 缺陷

### 11.1 执行计划仍需 app 手工组合

虽然原语已经通用化，但复杂 nearest route 仍需要 app/runner 选择：

- seed strategy；
- grid shape；
- inline threshold；
- exact-witness 或 fast-scalar；
- warmup protocol；
- partner/backend。

未来需要更明确的计划器或策略层，让用户描述输出合同和成本目标，由系统选择
执行位置与算法。

### 11.2 Prepared 生命周期没有完全语言化

fresh、long-lived process、explicit warmup 和 replay 的成本需要 runner 手工
记录。RTDL 应进一步提供正式的：

```text
prepare
bind input
execute query batch
reuse workspace
release
```

生命周期和可观测计时边界。

### 11.3 Device residency 仍不是整条路线的默认保证

X-HD 已减少大量 host row materialization，但输入加载、部分 seed/reference、
partner fallback 和结果比较仍可能跨 host/device。

系统需要更强的列所有权、stream ordering、lifetime 和 device-residency
metadata，使“没有 host bounce”成为可验证属性，而不是路线自述。

### 11.4 Backend capability 模型不足

Numba、Triton、CuPy、native CUDA 和 OptiX 的可用性、PTX/driver 兼容和性能
特征不同。当前选择仍包含环境特例。

RTDL 需要：

- backend capability query；
- version/ABI compatibility report；
- compile cache 与 fallback policy；
- 同一算子的多 backend contract parity gate。

### 11.5 近似/提前终止合同需要语言级表达

`per_source_witness_exact` 目前主要通过结果 metadata 传播。更成熟的语言模型应
让用户声明：

```text
exact scalar only
exact scalar + exact witness
bounded approximate witness
early termination allowed
```

编译器和 planner 才能合法选择 global-bound early-break 等优化。

## 12. 对 RTDL 发展方向的影响

X-HD 强化了 RTDL 的正确定位：

> RTDL 不是一个收集论文专用 kernel 的库，而是一门让用户组合空间关系、
> witness、frontier 和 reduction，由系统选择后端与执行策略的语言。

短期应继续巩固：

1. 通用 columnar point/frontier/worklist contracts；
2. exact/approximate result contract；
3. prepared execution 生命周期；
4. backend capability 与 fallback；
5. 非 app 消费者门；
6. fresh/warm/process/route 统一但不混淆的计时模型。

不应继续：

1. 为单篇论文增加 core identity；
2. 追逐无可达下游的作者内部 artifact parity；
3. 用 warm/replay 数字替代 fresh 用户成本；
4. 把 scalar 正确说成完整 witness 正确；
5. 在分母未对齐时报告 speedup。

## 13. 最终评价

X-HD 对 RTDL 的考核是成功的。

正确性上：

```text
7 / 7 primary same-input exact-witness cases matched
3 / 3 additional scalar-only routes matched
directed semantics behaviorally proved
```

架构上：

```text
Hausdorff remains an app composition
X-HD-specific core primitive added = false
generic nearest/max-nearest pipeline has a non-X-HD consumer
```

性能工程上：

```text
representative scalar route improved from about 7.30s to about 0.84s
full RTDL gate improved from about 10.01s to about 1.52s
author ratio remains unauthorized
```

治理上：

```text
author artifact-parity line fail-closed
exact paper artifact absence no longer misrepresented as solved
owner-approved same-input scope externally reviewed and closed
```

最重要的系统产物不是 X-HD app 本身，而是以下可复用执行骨架：

```text
generic spatial candidate generation
-> generic nearest state and witness
-> generic native frontier traversal
-> generic max-nearest reduction
-> app-owned interpretation and comparison
```

这条骨架可以继续服务 kNN、覆盖半径、设施选址、最差服务距离、空间过滤和其他
多阶段空间查询。X-HD 完成了 paper app 应有的任务：它是一张严格考卷，而留下
的是语言能力。

## 14. 主要证据

最终 closeout：

```text
history/internal_docs/goal5451_xhd_same_input_hdresult_closeout_2026-07-10.md
history/internal_docs/review_goal5451_xhd_same_input_hdresult_closeout_verified_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5451_same_input_hdresult_closeout.json
```

系统抽取：

```text
Goals5127-5128
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
```

性能与执行演化：

```text
Goals5188-5217
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5217_level_b_same_pod_performance_matrix_2026-07-09.json
```

治理与止损：

```text
history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md
history/internal_docs/owner_scope_decision_xhd_same_input_hdresult_sufficient_2026-07-10.md
```
