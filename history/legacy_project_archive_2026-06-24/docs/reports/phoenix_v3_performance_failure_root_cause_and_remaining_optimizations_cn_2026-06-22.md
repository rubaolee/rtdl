# Phoenix V3 性能失败根因与剩余优化计划

Date: 2026-06-22
Status: `technical_accounting_not_release_authorization`
Scope: Phoenix V3 only. V4 / C ABI / embedding / external zero-copy interop are out of scope.

## 0. 控制性结论

Phoenix V3 当前没有 release-level 性能证明。

同一套 RTX 4000 Ada RT 硬件、同一批 serious benchmark apps、V2.14 vs
Phoenix V3 的控制性结果是：

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
当前 Phoenix V3 在所有可比 serious 指标的几何平均上只比 V2.14 快约 1.2%。
这不是 major version 性能结果，而是接近平局。
```

App-level geomean：

| App | V3 vs V2.14 | 分类 |
| --- | ---: | --- |
| `hausdorff_xhd` | 1.149x | 明确正信号，但单 app 不足以支撑 V3 |
| `raydb_style` | 1.046x | 弱正信号，低于 major-version 级别 |
| `spatial_rayjoin` | 1.027x | 弱正信号，且 public RayJoin wording 仍被禁止 |
| `contact_manifold` | 1.017x | parity |
| `rtnn` | 1.003x | parity |
| `robot_collision` | 0.993x | parity / 轻微回退 |
| `rt_dbscan` | 0.988x | 轻微回退 |
| `triangle_counting` | 0.987x | 轻微回退 |
| `librts_spatial_index` | 0.937x | 回归 |
| `barnes_hut` | 0.844x | serious run 回归，后续 focused 修复只恢复到 parity/slight win |

当前负责结论：

```text
Phoenix V3 remains redo_required.
```

## 1. V3 要解决的性能问题

V2.x 证明了很多单独 RT-backed primitive 可以跑。Phoenix V3 必须解决的不是
“再做几个 benchmark app”，而是把 RTRDL 变成用户可以依赖的高性能语言/运行时：

```text
prepare once
reuse prepared handles
keep multi-phase work resident where the V3 contract allows
run typed continuations without Python row materialization dominating
account all phases honestly
expose this through a shared runtime surface, not app-local fast paths
```

因此，一个优化只有同时满足下面条件，才算 V3 级性能进展：

```text
generic runtime/language mechanism
productized execution path visible
same mechanism works on more than one Set-A probe or has a clear generalization path
same-RT-hardware evidence
material speedup, not just parity repair
all release/public/broad claim flags remain false until the gates authorize
```

## 2. 已做优化总账

| 优化 | 当前状态 | 目前效果 | 技术分类 |
| --- | --- | --- | --- |
| Prepared execution/session runner M1-M1.2 | 已实现并接入 fixed-radius grouped-stream route | grouped-stream pod A/B `0.998x`，中性 | 产品化路径/审计面 |
| AABB native query-handle runner M2/M2.1 | 已实现并在 pod 上有 focused 正证据 | OptiX/Embree cold-plus-collect `1.346x`，query-total `1.738x` | 第一个 material productized Set-A probe |
| RTDBSCAN component-signature runner M3/M3.1 | 已实现并接入 route | M3.1 runner-vs-legacy `0.5038x`，失败 | 产品化路径负证据 |
| Runner fingerprint/overhead fix M3.2 | 已实现并 pod A/B | runner-vs-legacy 从 `0.5038x` 修到 `0.9930x` | parity recovery |
| Repeated prepared-session runner M3.3 | 已实现，本地测试/Claude review 完成 | 18 focused tests OK；后续 M3.4 pod A/B 证明它可保持 RTDBSCAN parity，但不是 material win | 通用 runner 结构修复 |
| RTDBSCAN repeated-runner route M3.4 | 已实现并完成 focused pod A/B | runner-vs-legacy `0.9976x`，runner-vs-Embree `2.9416x`，不是 material Set-A candidate | parity recovery；停止作为第二 Set-A probe |
| Barnes-Hut prepared OptiX symbol/cache repair | 已实现并 focused pod evidence | serious losses `0.622x/0.591x` 修到 `0.999x/1.038x` | 回归修复 |
| LibRTS AABB count packing/symbol cache | 已实现并 focused evidence | Embree regression recovered；OptiX AABB unstable/inconclusive | 回归修复 |
| RTNN neighbor symbol/cache repair | 已实现并 focused evidence | 12-row geomean `1.001x` | 无 material speedup hygiene |
| Fixed-radius symbol/library cache broadening | 已实现并 focused evidence | 17-row geomean `1.062x` | 有用 cleanup，但不够 release |
| Fixed-radius graph self-query refresh | 已实现并 focused evidence | 3-row CuPy A/B `0.998x` | residency/contract cleanup，无 material speedup |
| RTNN repeat50 hot-query route | 已有 evidence | hot-query `7.889x`，cold-plus-query `1.315x`，runner-wall `3.761x` | 有 hot-query upside，但必须披露 cold/wall |
| RayDB grouped reduction rows | 已有 row-scoped evidence | app geomean `1.046x` | reusable continuation 线索，未完全产品化 |
| Triangle prepared graph chunk | 已有 row-scoped evidence | app geomean `0.987x` | prepared graph 未产品化成通用图编译器 |
| Spatial topology stream | 已有 row-scoped evidence | app geomean `1.027x` | topology stream 线索，public wording blocked |

## 3. 没有给出性能的优化：为什么期待、为什么失败

### 3.1 Runner M1-M1.2：路径产品化了，但没变快

当初期待：

```text
V3 不能只有 benchmark 内部 fast path。
用户需要一个 shared runner 来承载 backend、partner、cache、phase、residency metadata。
```

目前效果：

```text
grouped-stream route pod A/B geomean: 0.9979x
```

为什么没有形成性能：

```text
M1-M1.2 先解决的是“路径可见、可审计、可产品化”，不是“runner hot path 足够便宜”。
在已经很快的 legacy route 外面包 runner，如果 runner 每次 repeat 都做 cache/report/fingerprint，
结果很容易只是 parity 或略慢。
```

结论：

```text
方向正确，但不是性能证明。它是后续通用优化的承载层。
```

### 3.2 RTDBSCAN M3.1：产品化 runner 输给 incumbent legacy OptiX

当初期待：

```text
RTDBSCAN component-signature 是典型 Set-A multi-phase / continuation-rich workload。
如果 runner 能把 fixed-radius graph + component signature 产品化，应该成为第二个 Set-A material win。
```

目前效果：

```text
M3.1 runner_vs_legacy: 0.5038x
M3.1 runner_vs_embree: 1.4917x
```

为什么没有形成性能：

```text
错误的诱惑是看 runner_vs_embree。
真正相关的 incumbent 是 legacy OptiX grouped-stream route。
runner 产品化路径比 legacy OptiX 多了 wrapper/fingerprint/report/repeat-loop 成本，
所以虽然仍然比 Embree 快，却没有打败 V2/V3 已有的 OptiX incumbent。
```

结论：

```text
这是有效负证据，不是可宣传 speedup。
```

### 3.3 RTDBSCAN M3.2：大修有效，但只修回 parity

当初期待：

```text
M3.1 的 0.5038x 太低，像 runner overhead 而不是 RT traversal 本身失败。
_stable_input_fingerprint 的大 sequence repr/truncation 成本和 cache-key 风险是明确嫌疑点。
```

目前效果：

```text
runner_vs_legacy: 0.5038x -> 0.9930x
runner_vs_embree: 2.934x
```

为什么没有形成 V3 性能：

```text
M3.2 证明 overhead 修复有效，但结果是 parity recovery。
它把 V3 从“产品化路径明显更慢”修到“几乎不比 legacy 慢”，
没有证明产品化路径 materially faster。
```

结论：

```text
必须保留，但不能当作 major-version speedup。
```

### 3.4 Symbol/cache 修复：多数是清理 V3 自己引入的 overhead

当初期待：

```text
native library/symbol lookup、prepared query packing、重复 handle setup 是纯 overhead。
这些成本在 repeated/prepared workloads 中应该可以被缓存或复用。
```

目前效果：

```text
Barnes-Hut OptiX losses: 0.622x/0.591x -> 0.999x/1.038x
LibRTS Embree count-only regression: recovered
RTNN symbol/cache focused geomean: 1.001x
Fixed-radius 17-row focused geomean: 1.062x
```

为什么没有形成 V3 性能：

```text
这些优化大多是在移除 V3 自己引入或暴露的 overhead。
它们的自然上限往往是“V3 不再比 V2.x 慢”，而不是“V3 显著比 V2.x 快”。
RTNN 的 1.001x 说明瓶颈根本不在 symbol lookup。
```

结论：

```text
必要工程卫生，但不足以支撑 V3。
```

### 3.5 Fixed-radius graph self-query refresh：更诚实、更 resident，但不快

当初期待：

```text
把 grouped-stream core-flag refresh 从 host query-point upload 改成 prepared self-query device-search columns，
应该减少 host boundary，并改善 device-residency story。
```

目前效果：

```text
3-row CuPy A/B geomean: 0.998x
metadata/contract: improved
```

为什么没有形成性能：

```text
这个改动主要改变数据路径的诚实性和 residency metadata。
在当前规模/route 下，减少的 host-boundary 成本不足以超过额外路径成本或测量噪声。
```

结论：

```text
这是 contract cleanup，不是 material speedup。
```

### 3.6 RTNN hot-query：局部很快，但不是完整用户体验

当初期待：

```text
prepared ranked-summary repeat50 应该从 prepare once / query many 获益。
这是 V3 要证明的 prepared-session 使用模型。
```

目前效果：

```text
hot-query: 7.889x
cold-plus-query: 1.315x
runner-wall: 3.761x
RTNN symbol-cache focused 12-row geomean: 1.001x
```

为什么没有形成 broad 性能：

```text
hot-query 不能单独代表用户可见 end-to-end。
如果 setup/packing/load/final summary 没有被 amortized prepared-session contract 明确管理，
hot-query speedup 会被 cold/wall 成本稀释。
```

结论：

```text
RTNN 仍有 V3 线索，但必须做 setup/packing amortization 和三数披露，不能只报 hot-query。
```

### 3.7 Row-scoped continuation / graph / topology wins：有线索，未产品化

当初期待：

```text
RayDB grouped reduction、RTDBSCAN component union、Triangle chunk、Spatial topology stream
都符合 V3 的真实方向：RT traversal 产生 candidates，typed continuation 在 device/column 侧总结，
减少 Python row materialization。
```

目前效果：

```text
RayDB app geomean: 1.046x
RTDBSCAN app geomean: 0.988x
Triangle app geomean: 0.987x
Spatial app geomean: 1.027x
```

为什么没有形成 V3 性能：

```text
这些还是 row-scoped / route-specific evidence。
V3 作为语言/runtime，不能靠单个 benchmark route 的特殊正信号成立。
需要 shared continuation contract、shared execution path，并且同一机制在多个 Set-A probes 上赢。
```

结论：

```text
保留为技术线索，但不能当作 release proof。
```

## 4. 当前唯一比较硬的正证据

### 4.1 Hausdorff app-level 正信号

```text
hausdorff_xhd app geomean: 1.149x
```

意义：

```text
说明 fixed-radius / threshold-style 路线确实有部分 V3 正收益。
```

不足：

```text
单 app 不足以支撑 major release；也不能证明 shared productized runtime 广泛赢。
```

### 4.2 AABB M2.1 productized runner focused win

```text
OptiX / Embree cold-plus-collect wall speedup: 1.346x
OptiX / Embree query total speedup: 1.738x
productized_execution_path: prepared_execution_session_runner
runtime_executed_count: 50
cache_hit_count: 49
```

意义：

```text
这是当前最强的 productized-path focused evidence。
它证明 shared runner + prepared native query-handle reuse 可以在真实 RT 硬件上产生 material win。
```

不足：

```text
它只是第一个 Set-A material probe。
Gate 要求至少两个 productized-path material probes，且不能直接推出 full V3 release。
```

## 5. 剩余要实现的优化，以及为什么仍然值得期待

### 5.1 M3.4 focused pod A/B：已完成，验证结果是 parity 不是 material win

状态：

```text
M3.3 repeated prepared-session runner: implemented locally
M3.4 RTDBSCAN route wiring: implemented locally
Claude verdict: approve_route_contract_not_release
focused_m3_4_pod_ab_authorized: true
focused_m3_4_pod_ab_completed: true
runner_vs_legacy_geomean: 0.997557675600175
runner_vs_embree_geomean: 2.941644953697829
legacy_parity_recovered: true
material_set_a_candidate: false
```

要验证：

```text
runner elapsed_override = median(measured_repeat_seconds[i] + column_signature_sec[i])
legacy elapsed_override = median(perf_counter window including native call + signature)
```

为什么值得期待：

```text
M3.2 已经把 runner-vs-legacy 从 0.5038x 修到 0.9930x。
M3.4 删除 app-level per-repeat runner call loop，
如果剩余 overhead 主要来自 repeated wrapper/report/cache，那么它可能把 parity 推到 material gain。
```

实际结果：

```text
runner_vs_legacy = 0.997557675600175
classification = parity-preserving progress only
second_material_set_a_probe_obtained = false
```

动作：

```text
M3.4 不 material，因此停止继续围绕 RTDBSCAN 微调。
转向 AABB generalization 或 typed continuation runner。
```

### 5.2 AABB runner generalization：把唯一强正证据变成通用 primitive family

要实现：

```text
把 M2.1 的 prepared native query-handle reuse 从 Contact Manifold harness 中抽成更通用 AABB primitive family。
至少再接一个 AABB-style workload，保持同一 runner contract 和 phase accounting。
```

为什么值得期待：

```text
AABB M2.1 已经在 pod 上显示 1.346x cold-plus-collect 和 1.738x query-total。
如果同一 mechanism 在第二个 AABB workload 上仍然 material，
它就从“一个 harness 上的 win”升级为“V3 generic AABB runtime primitive evidence”。
```

成功标准：

```text
same generic AABB primitive family
same prepared_execution_session_runner metadata
no app-specific native engine
>= 1.15x focused material speedup against the relevant incumbent/control
```

### 5.3 Productized typed continuation runner：把 row-scoped wins 变成 shared V3 contract

要实现：

```text
generic grouped reduction / component signature / compact summary contracts
typed/device-column inputs
explicit partner
no hidden automatic partner selection
hot path avoids Python row materialization unless output contract requires it
```

为什么值得期待：

```text
M0-M149 里反复出现的强线索是：
RT traversal produces candidates -> typed continuation summarizes candidates -> Python rows are avoided.
RayDB、RTDBSCAN、Spatial、Triangle 的内部证据都指向这个模式。
问题不是模式无效，而是它没有成为 shared runtime surface。
```

成功标准：

```text
same continuation contract used by at least two probes
at least one focused Set-A material win
second probe parity-or-better
all phase/accounting metadata present
```

### 5.4 Device-resident internal phase contract：不再把 host boundary 藏起来

要实现：

```text
phase-to-phase state stays as device/column data where allowed
host materialization occurs only at final output or explicit benchmark contract boundary
phase report names every host boundary
```

为什么值得期待：

```text
V3 真正应该赢的是 multi-phase workload。
如果 traversal 后马上回 host，再由 Python 组织下一阶段，
RT core traversal 的收益会被 materialization 和 data movement 吞掉。
```

成功标准：

```text
Set-A material win comes from reduced host boundary/residency, not just cache trick
phase accounting shows prepare/query/continuation/finalize separately
no hidden hot-phase host materialization
```

### 5.5 RTNN setup/packing amortization：只在三数都改善时保留为 pillar

要实现：

```text
prepared input package reuse
column residency across repeated ranked-summary queries
explicit amortized-prepared mode
separate load / pack / prepare / query / continuation / final summary accounting
```

为什么值得期待：

```text
RTNN hot-query 7.889x 说明核心 prepared query 有 upside。
但 1.001x symbol-cache result 说明瓶颈不在 symbol lookup。
真正可期待的地方是 setup/packing amortization，而不是继续修 symbol cache。
```

成功标准：

```text
hot-query, cold-plus-query, runner-wall all reported
wall-level improvement, not hot-only claim
```

## 6. 现在必须停止或降级的工作

这些不能继续作为 Phoenix V3 性能策略：

```text
isolated app-specific patch
symbol-cache-only work after route reaches parity
hot-query-only claim
OptiX-vs-Embree claim when the real question is V3-vs-V2 or runner-vs-incumbent
public RayJoin/Spatial wording without result-count and paper-scope proof
full all-app pod rerun before at least two material productized Set-A probes exist
V4 / C ABI / embedding / SDK / external zero-copy work inside V3
```

## 7. 推荐剩余工作顺序

1. Treat M3.4 as completed parity evidence, not material Set-A evidence.
2. Stop RTDBSCAN as the immediate second material path.
3. Generalize AABB M2.1 into a shared AABB primitive family and test a second AABB-style probe.
4. Productize typed continuation runner for grouped reduction/component signature/compact summary.
5. Only after at least two productized-path Set-A material probes exist, reconsider full all-app V2.14 vs V3 pod run.

Hard stop rule:

```text
If the next two productized-path Set-A attempts cannot produce material focused evidence,
stop Phoenix V3 performance implementation and write a redesign handoff instead of stacking more app patches.
```

## 8. Current Authorization State

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_m3_4_pod_ab_authorized: true
focused_m3_4_pod_ab_completed: true
second_material_set_a_probe_obtained: false
```

## 9. Goal-Level Decision Audit

Decision: record a hard technical document explaining why Phoenix V3 currently
has no release-level performance, what optimizations were already done, why many
failed to produce material speedup, and what remaining generic optimizations are
still worth doing.

1. Was I foolish?
   No for this decision. It starts from the failed `1.011779x` same-hardware evidence rather than trying to protect an old release story.
2. If yes, what actions made the decision foolish?
   The foolish actions would be: calling parity recovery a major-version win, quoting OptiX-vs-Embree when the relevant comparison is V3-vs-V2 or runner-vs-incumbent, or continuing app-specific patches as if they were language/runtime optimization.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. Freeze broad claims, separate Set A from Set B, require productized-path focused evidence, and stop any path that only reaches parity.
4. Can I now try a different path that truly solves the problem?
   Yes. The different path is to implement and measure generic runner/residency/typed-continuation mechanisms, with focused pod A/B before any full all-app rerun.

## 10. Sources

- `docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- `docs/reports/phoenix_v3_no_performance_optimization_technical_accounting_cn_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_pod_ab_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719/summary.json`
- `docs/reviews/claude_phoenix_v3_rtdbscan_repeated_runner_route_m3_4_review_2026-06-22.md`
- `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`
