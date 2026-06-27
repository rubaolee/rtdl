# Phoenix V3 无性能证明下的优化技术账本

Date: 2026-06-22
Status: `technical_accounting_not_release_authorization`
Scope: Phoenix V3 only. V4 / C ABI / embedding / external zero-copy interop are out.

## 0. 结论

现在的 Phoenix V3 没有 release-level 性能证明。

同一套 RTX 4000 Ada 硬件、同一批 serious benchmark apps、V2.14 vs
当前 Phoenix V3 的控制性结果是：

```text
evidence_dir: docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100
same_metric_comparison_count: 52
v3_geomean_speedup_vs_v2: 1.0117790403434224
v3_faster_count_gt_5pct: 12
v3_slower_count_gt_5pct: 5
similar_count_within_5pct: 35
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

直接解释：

```text
当前 V3 在所有可比指标的 blended geomean 上只比 V2.14 快约 1.2%。
这不是 major version 的性能结果，而是接近平局。
```

App-level geomean：

| App | V3 vs V2.14 | 读法 |
| --- | ---: | --- |
| `hausdorff_xhd` | 1.149x | 唯一明确超过 1.05x 的 app-level 正信号 |
| `raydb_style` | 1.046x | 有正信号，但低于 major-version 级别 |
| `spatial_rayjoin` | 1.027x | 弱正信号，且不能公开宣称 RayJoin 胜利 |
| `contact_manifold` | 1.017x | 基本 parity |
| `rtnn` | 1.003x | parity |
| `robot_collision` | 0.993x | parity / 轻微回退 |
| `rt_dbscan` | 0.988x | 轻微回退 |
| `triangle_counting` | 0.987x | 轻微回退 |
| `librts_spatial_index` | 0.937x | 回归 |
| `barnes_hut` | 0.844x | serious run 回归；后续有 focused 修复证据 |

所以当前负责的结论是：

```text
Phoenix V3 remains redo_required.
```

这个文档的目的不是美化 V3，而是回答三个问题：

1. 我们已经做过哪些优化？
2. 为什么当初期待它们有效，但实际没有形成 V3 级性能？
3. 剩下还应该做哪些通用引擎优化，为什么这些仍然值得期待？

## 1. V3 要解决的性能问题

V2.x 证明了很多单独 RT-backed primitive 可以跑。V3 应该解决的是更高一层的问题：

```text
把单点 primitive 变成用户可依赖的高性能 RTRDL language/runtime：
prepare once, reuse handles, keep internal phases resident, run typed
continuations, account phases honestly, and expose the path through a shared
runtime surface instead of one-off benchmark code.
```

因此，V3 的有效优化必须满足两个条件：

- 它是通用 runtime/language 机制，不是 app 专门 patch；
- 它能在 serious evidence 上带来 material speedup，而不只是修回 parity。

## 2. 已做优化清单

| 优化 / 路线 | 分类 | 当初为什么期待有效 | 当前效果 | 为什么没有形成 V3 级性能 |
| --- | --- | --- | --- | --- |
| `prepared_execution_session_runner` M1-M1.2 | 运行时产品化表面 | V3 不能只有 benchmark 内部 fast path；用户应该通过共享 runner 获得 backend / partner / cache / phase / residency metadata | runner 已建立并接入 grouped-stream 与 AABB route；grouped-stream pod A/B 约 `0.998x` | 先解决了“路径可见和可审计”，没有先解决“runner 足够便宜”。第一条 route 基本中性。 |
| Fixed-radius prepared symbol/library cache | 回归修复 / shared primitive cleanup | Hausdorff、RTDBSCAN、Barnes-Hut、RTNN 都复用 fixed-radius / neighbor style primitive；重复 native symbol/library lookup 是纯 overhead | focused 17-row packet `1.062x` geomean；OptiX subset `1.119x` | 有用，但集中在部分 fixed-radius rows，尤其 Hausdorff；不能覆盖全 app，也不是 broad V3 proof。 |
| Barnes-Hut prepared OptiX symbol/cache repair | 回归修复 / parity recovery | serious run 的 Barnes-Hut OptiX 回退像 runtime overhead，不像算法失败 | old serious losses 从 `0.622x -> 0.999x`、`0.591x -> 1.038x`、`0.961x -> 0.990x` | 这是必要修复，但主要把 V3 从严重回归修到 parity。parity recovery 不是 major-version speedup。 |
| LibRTS AABB count packing/symbol cache | 回归修复 | AABB count-only 重复 packing / symbol lookup 应该可以由 prepared query reuse 避免 | focused evidence 中 Embree count-only regression recovered；OptiX AABB row 仍 unstable / inconclusive | 修复了一个 shared AABB path 的一部分，但没有证明所有 backend / app breadth。 |
| AABB native query-handle runner M2.1 | productized-path focused win | repeated AABB queries 应该受益于 prepared native query handle reuse，且通过 productized runner 记录 phase/cache | 32,768 row cold-plus-collect `1.719x`、query-total `1.867x`；65,536 row cold-plus-collect `1.637x`、query-total `1.743x`；six fresh runs weakest cold-plus-collect `1.644x` | 这是当前最强正证据，但只有一个 focused probe。它证明“有一个机制能赢”，还没证明“V3 runtime broadly wins”。 |
| RTDBSCAN component-signature runner M3.1 | productized runner negative evidence | component-union/component-signature 是通用 continuation；通过 runner 应该替代 legacy app route | M3.1 runner-vs-legacy geomean `0.5038x`；runner-vs-Embree `1.4917x` | 相关 incumbent 是 legacy OptiX，不是 Embree。runner wrapper overhead 太大。 |
| RTDBSCAN fingerprint/overhead fix M3.2 | runner parity recovery | M3.1 显示 native grouped work 接近 legacy，但 wrapper overhead 大；hot loop 内大 sequence fingerprint/repr 是可疑成本和 cache-key 风险 | runner-vs-legacy 从 `0.5038x` 修到 `0.9930x`；runner-vs-Embree `2.934x` | 这是好修复，但结果是 parity recovery，不是第二个 material Set-A win。 |
| RTNN prepared repeat50 hot-query route | row-scoped amortized prepared evidence | prepared ranked-summary repeated queries 应该从 prepare once / query many 中获益 | reviewed evidence: `7.889x` hot-query、`1.315x` cold-plus-query、`3.761x` runner-wall over named CuPy reference | 有价值，但必须三数一起报告。hot-query 快不等于用户 end-to-end 快。 |
| RTNN neighbor symbol/cache repair | cleanup without material speedup | 如果 RTNN 慢在 symbol lookup，缓存应提升 stress-scale RTNN | focused 12-row geomean `1.001x` | 瓶颈不在 symbol lookup；setup/packing/contract shape 更可能主导。 |
| Fixed-radius graph self-query device-search refresh | residency / contract cleanup | self-query path 避免 host query-point repack/upload，应该更 device-resident | 3-row CuPy A/B geomean `0.998x`，metadata 更诚实 | 改善 contract honesty，但没有 material speedup。 |
| RayDB grouped reduction rows | row-scoped continuation | grouped reduction 是通用 continuation；device/scalar rows 应减少 Python materialization | RayDB app geomean `1.046x`，有内部 reusable grouped_reduction evidence | 没有完全产品化为 shared continuation runtime；不是 database product speedup。 |
| RTDBSCAN component-union row | row-scoped continuation | component union / signature 应避免大量 host neighbor rows | serious app geomean `0.988x`；M3.2 runner parity only | 不是 full RTDBSCAN speedup，也不是 material productized runner win。 |
| Triangle prepared graph chunk | row-scoped prepared graph | prepared graph/chunk execution 应 amortize graph setup | Triangle app geomean `0.987x`；只有 exact row 内部证据 | prepared graph 没成为通用生产级执行图；单行不等于语言 release。 |
| Spatial topology stream | row-scoped topology stream | stream topology / point-location status 应替代 host relation-status work | Spatial app geomean `1.027x`，有 row-level signal | result-count / paper-scope / public RayJoin wording 都没闭环。不能作为公开 Spatial/RayJoin 胜利。 |
| Barnes-Hut fused / explicit partner route | row-scoped partner continuation | RTDL 可以把 compact candidates 交给 explicit partner 做 continuation | 有 partner route evidence | 需要产品化为 shared continuation contract；否则只是 benchmark route。 |

## 3. 为什么当初期待有效

这些优化方向本身不是错的。它们对应真实的 runtime 成本：

- repeated native symbol lookup / library lookup 是纯 overhead；
- repeated prepare/query/report loop 会浪费 prepared scene / handle 的价值；
- Python row materialization 会吞掉 RT traversal 的收益；
- multi-phase workload 如果在 RTDL 内部不断回 host，就很难赢；
- grouped reduction、component union、topology stream、ranked summary 都是可复用 continuation pattern；
- phase accounting 可以防止我们把 cold/setup 成本藏在 hot-query 之外。

也就是说，V3 的方向是合理的：

```text
prepare once -> keep work resident -> run typed continuation -> report phases honestly
```

真正的问题不是“这些想法一定错”，而是当前完成度没有把这些想法变成 broad user-visible performance。

## 4. 为什么实际没有效果

### 4.1 大量优化只是把 V3 修回 V2.x parity

Barnes-Hut、LibRTS、RTDBSCAN M3.2、fixed-radius symbol cache 都说明一件事：

```text
很多工作是在移除 V3 自己引入的 overhead。
```

这类修复必须做，但上限通常是：

```text
V3 no longer slower than V2.x.
```

不是：

```text
V3 is materially faster than V2.x.
```

M3.2 最典型：

```text
RTDBSCAN M3.1 runner_vs_legacy: 0.5038x
RTDBSCAN M3.2 runner_vs_legacy: 0.9930x
```

这说明修复有效，但只恢复 parity。

### 4.2 Hot-query 证据被误读为用户可见速度

RTNN repeat50 证明 hot query 可以很快：

```text
hot-query: 7.889x
cold-plus-query: 1.315x
runner-wall: 3.761x
```

但 stress-scale RTNN symbol-cache rerun 是：

```text
focused 12-row geomean: 1.001x
```

结论是：如果 V3 没有把 amortized prepared session 做成明确用户契约，hot-query 不能单独作为 release speedup。

### 4.3 Row-scoped wins 没有产品化成 shared runtime wins

RayDB grouped reduction、RTDBSCAN component union、Triangle chunk、Spatial topology stream 都是有意义的内部证据。

但 V3 作为语言/runtime，不能靠“某个 benchmark route 正好快”成立。需要的是：

```text
shared execution path
shared continuation contract
same mechanism wins on multiple probes
```

当前还没有足够证据证明这个链条成立。

### 4.4 Productized runner 先变得可见，但还没普遍变快

runner 是正确方向，因为它把这些信息变成可审计 runtime surface：

- backend；
- partner；
- cache hit/miss；
- phase timing；
- runtime execution；
- release/public claim flags。

但 runner 如果给 hot path 加 overhead，就不能成为性能故事。

AABB M2.1 说明 runner 可以赢；RTDBSCAN M3.1/M3.2 说明 runner 还没普遍赢。

### 4.5 Blended geomean 混合了不同类型 workload

`1.011779x` blended geomean 是 release blocker，必须保留。但工程诊断上，它混合了：

- multi-phase / residency / continuation-rich workloads；
- single-shot / materializing controls；
- row-scoped capability probes；
- app-level end-to-end routes；
- hot-query and cold/wall measurements。

所以之后必须同时看：

- Set A：V3 应该通过 productized path material wins 的 workload；
- Set B：V3 应该保持 parity，并解释 ceiling / control workload。

当前 frozen Set A/B gate：

```text
Set A geomean: 1.012934x
Set B geomean: 1.006943x
Set A apps over 1.05x: 1 / 5 required
Set A severe regression: barnes_hut at 0.8441965x
Set B sub-0.95 row: librts_embree_aabb_index
focused material productized probes: 1 / 2 required
all_app_pod_spend_authorized: false
```

## 5. 当前真正有价值的正证据

| 证据 | 为什么重要 | 为什么还不够 |
| --- | --- | --- |
| `hausdorff_xhd` app geomean `1.149x` | serious run 中唯一明确 app-level >1.05x 的正结果 | 一个 app 不能支撑 V3 major release |
| AABB M2.1 runner-backed focused result | 当前第一个 material productized-path win | 只有一个 focused probe；还需要第二个和外部 review / gate |
| RTDBSCAN M3.2 parity recovery | 证明 generic fingerprint/overhead 修复有效 | parity 不是 material win |
| RayDB grouped rows | 证明 grouped continuation 有潜力 | 还不是 shared continuation runtime |
| Barnes-Hut focused repair | 证明 V3 regressions 能被定位并修复 | 回归修复不是 major-version speedup |

因此当前状态是：

```text
material_set_a_runner_backed_probe_count: 1
second_material_probe: missing
full_all_app_pod_spend_authorized_now: false
release_authorized: false
```

## 6. 剩余应实现的优化

以下都是通用语言/runtime 优化，不是 app-specific benchmark patch。

### 6.1 Repeated prepared-session execution API

要实现：

- one prepared task；
- one cache lookup；
- one prepared handle；
- warmup + measured repeats 在 runner 内部完成；
- measured loop 内不重复 fingerprint / report / task reconstruction；
- 一次性输出 cold、warmup、measured median、validation、phase metadata。

为什么值得期待：

legacy fast routes 手写的快路径通常就是这个结构。runner 如果不能匹配这个结构，就会在产品化时输给 legacy route。M3.1/M3.2 已经证明 wrapper overhead 能从 `0.5038x` 修到 `0.9930x`，所以继续去掉 per-iteration overhead 是有明确机制的。

成功条件：

```text
runner metadata present
runtime_executed: true
runner-vs-legacy >= 0.98x for repaired routes
runner-vs-legacy >= 1.15x before calling it a material Set-A win
claim flags remain false
```

失败条件：

```text
如果 repeated runner 去掉 per-iteration overhead 后仍只接近 1.00x，
则此路径只能算 parity repair，不能继续当作 V3 speed thesis。
```

### 6.2 Productized typed continuation runner

要实现：

- typed/device columns as input；
- generic grouped reduction / component union / compact summary contracts；
- 尽量在 device/column summary 中完成输出；
- hot path 不 materialize Python rows；
- partner 必须 explicit，不能隐藏成自动魔法。

为什么值得期待：

M0-M149 中最强的行级证据反复来自同一模式：

```text
RT traversal produces candidates
typed continuation summarizes candidates
Python row materialization is avoided
```

如果这个模式产品化为 shared continuation runner，并在至少两个 probes 上成立，它才有资格成为 V3 runtime story。

成功条件：

```text
same continuation contract used by >= 2 probes
one probe material Set-A win
second probe parity-or-better
no app-specific native symbol
```

失败条件：

```text
如果胜利来自改变某个 benchmark 语义或加入 app-shaped native shortcut，
结果必须 rejected。若所有 probes 只有 parity，则保留为 cleanup，不算 V3 material performance。
```

### 6.3 Device-resident internal phase contract

要实现：

- RTDL 内部 phase 之间尽量保留 device/column state；
- host materialization 只在最终结果或 benchmark contract 要求时发生；
- phase accounting 明确列出 host boundary；
- 不许把 host copy 藏在“prepared”或“continuation”名义下。

为什么值得期待：

V3 想赢的是 multi-phase workloads。如果 traversal 后马上回 host，再由 Python 组织下一阶段，RT core 的收益会被 data movement 和 materialization 吞掉。

成功条件：

```text
phase report shows no hidden hot-phase host materialization
same route reports prepare/query/continuation/finalize separately
Set-A route material win comes from residency, not cache trick
```

失败条件：

```text
如果 phase accounting 仍显示 RTDL-owned phases 之间有相同 host materialization，
则 V3 尚未实现 residency mechanism，不能继续做性能宣称。
```

### 6.4 AABB runner generalization

要实现：

- 把 AABB M2.1 的 prepared native query-handle reuse 做成 shared AABB primitive；
- Contact Manifold-style 和 LibRTS-style AABB workloads 使用同一 primitive；
- 保持 runner metadata 和 phase accounting；
- 不复制 app-specific AABB route。

为什么值得期待：

AABB M2.1 已经是当前最强 productized-path focused win：

```text
32768 cold-plus-collect: 1.719x
32768 query-total: 1.867x
65536 cold-plus-collect: 1.637x
65536 query-total: 1.743x
weakest fresh cold-plus-collect: 1.644x
```

如果同一机制在第二个 AABB probe 上仍成立，它就从“一个 route win”升级为“generic AABB runtime primitive evidence”。

成功条件：

```text
same generic AABB primitive family
same runner contract
>= 2 probes measured
no app-specific AABB engine
```

失败条件：

```text
如果第二个 probe 不保留 material wall speed，M2.1 仍保留为 row-scoped win，
但不能作为 broad V3 pillar。
```

### 6.5 RTNN setup/packing amortization

要实现：

- reusable prepared input package；
- column residency across repeated ranked-summary queries；
- explicit amortized-prepared mode；
- phase report 分离 load / pack / prepare / query / continuation / final summary；
- 不做 RTNN-specific native shortcut。

为什么值得期待：

RTNN 有 hot-query upside，但 cold/wall 被 setup/packing 吞掉。唯一诚实路径是把 amortized prepared usage 做成 V3 契约，或者直接减少 setup/packing。

成功条件：

```text
hot-query, cold-plus-query, runner-wall all reported
amortized-prepared mode documented and tested
wall-level improvement, not hot-only claim
```

失败条件：

```text
如果 hot-query 继续快，但 cold/wall 仍 parity 或更慢，
停止把 RTNN 作为 V3 performance pillar。
```

### 6.6 Frozen Set A / Set B gate

这不是性能优化，但它是下一次 pod 开销前的控制门。

要实现 / 保持：

- Set A：residency / multi-phase / continuation-rich probes，必须 material win；
- Set B：single-shot / materializing controls，必须 parity + explanation；
- classification frozen before run；
- new case IDs 必须预注册；
- surprising rows 必须解释。

为什么值得期待：

它防止再次出现一个 `~1.0x` blended geomean，把真正的 wins、regressions、controls 混在一起看不清。

成功条件：

```text
Set A geomean >= 1.20x before release consideration
Set A app wins > 1.05x meet the required count
Set B geomean >= 0.98x
no severe unexplained Set A regression
no unexplained Set B sub-0.95 row
```

## 7. 现在应该停止的工作

以下不应继续作为 V3 性能策略：

- isolated app rows that do not enter shared runner / continuation contracts；
- symbol-cache-only work after a route reaches parity；
- hot-query-only claims without cold/wall/amortization disclosure；
- OptiX-vs-Embree claims when the real question is V3-vs-V2 or runner-vs-incumbent；
- public Spatial / RayJoin claims without result-count, scope, and paper-basis proof；
- full all-app pod rerun before at least two material productized-path Set-A probes exist；
- any V4 / C ABI / embedding / SDK / host-zero-copy work inside Phoenix V3。

## 8. 推荐剩余工作顺序

1. 完成 repeated prepared-session runner，使 measured loop 内不重复构造 fingerprint/report/task。
2. 选择第二个 Set-A probe，优先从 AABB generalization 或 typed continuation runner 入手。
3. 对第二个 probe 做 focused same-pod A/B；只看 productized path vs incumbent route。
4. 如果第二个 probe material win 成立，更新 Set A/B gate；否则记录失败并换机制，不做 full all-app run。
5. 产品化 typed continuation runner，使 grouped reduction / component union 至少共用一个 contract。
6. 只有当至少两个 productized-path Set-A focused wins 存在，且 Set B blocker 解释/修复后，才授权新的 full all-app V2.14 vs V3 pod run。

停止规则：

```text
如果接下来两个 productized-path Set-A attempts 都不能产生 material focused evidence，
停止 Phoenix V3 性能工作，交付 redesign handoff，而不是继续堆 app patches。
```

## 9. Goal-Level Decision Audit

Decision: 在 V3 没有 release-level 性能的前提下，记录已经做过的优化、
失败原因、剩余可期待的通用引擎优化，并保持 release blocked。

1. Was I foolish?
   No for this decision. 这个决定从 failed same-hardware evidence 出发，而不是从想发布的愿望出发。
2. If yes, what actions made the decision foolish?
   会愚蠢的动作是：把 `1.012x` 说成成功，把 parity repair 说成 major speedup，把 OptiX-vs-Embree 当成 V3-vs-V2。
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. 正确路径是停止 app-by-app 美化，转向 productized runner、typed continuation、device-residency contract。
4. Can I now try a different path that truly solves the problem?
   Yes. 下一步只做 generic runtime work，并要求 focused Set-A pod evidence；没有第二个 material productized-path win，就不花钱跑 full all-app。

## 10. Sources

- `docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json`
- `docs/rebuild/v3/phoenix_v3_serious_v2x_paired_benchmark_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- `docs/reports/phoenix_v3_performance_failure_optimization_accounting_2026-06-22.md`
- `docs/reports/phoenix_v3_optimization_effectiveness_and_remaining_plan_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_performance_failure_accounting_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_performance_failure_accounting_2ai_consensus_2026-06-22.md`
