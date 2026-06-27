# Phoenix V3 Performance Failure And Optimization Accounting

Date: 2026-06-22
Status: `technical_accounting_not_release_authorization`
Scope: Phoenix V3 only. No V4, no C ABI, no embedding, no external zero-copy interop.

## 0. Executive Conclusion

Phoenix V3 currently has no release-level performance proof.

The controlling same-RT-hardware V2.14 vs Phoenix V3 result is:

```text
evidence_dir: docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100
same_metric_comparison_count: 52
v3_geomean_speedup_vs_v2: 1.0117790403434224
v3_faster_count_gt_5pct: 12
v3_slower_count_gt_5pct: 5
similar_count_within_5pct: 35
release_consideration_eligible: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Plain reading:

```text
Phoenix V3 is about 1.2% faster than V2.14 by the blended all-app geomean.
That is effectively parity, not a major-version performance result.
```

App-level geomeans:

| App | V3 vs V2.14 geomean | Reading |
| --- | ---: | --- |
| `hausdorff_xhd` | 1.149x | real positive app-level signal |
| `raydb_style` | 1.046x | modest, below a major-version bar |
| `spatial_rayjoin` | 1.027x | modest, partly row-specific |
| `contact_manifold` | 1.017x | parity |
| `rtnn` | 1.003x | parity |
| `robot_collision` | 0.993x | parity / slight loss |
| `rt_dbscan` | 0.988x | slight loss |
| `triangle_counting` | 0.987x | slight loss |
| `librts_spatial_index` | 0.937x | regression |
| `barnes_hut` | 0.844x | serious-run regression; later focused repair evidence exists |

Therefore the only responsible release state is:

```text
Phoenix V3 remains redo_required.
```

This document records what was optimized, why those optimizations were expected
to matter, what effect they actually had, why they did not produce V3-level
performance, and what remaining generic engine optimizations are still worth
implementing.

## 1. What V3 Was Supposed To Improve

Phoenix V3 was not supposed to be a collection of faster benchmark apps. RTDL is
the language/runtime; benchmark apps are probes used to develop and test the
language.

The V3 performance thesis was:

```text
V2.x proved many individual RT-backed primitives.
V3 should turn them into a more reusable high-performance execution layer:
prepare once, keep intermediate work resident, run typed continuations, and
measure phases honestly.
```

The major technical targets were:

- productized prepared execution/session runner;
- execution graph or prepared graph that actually executes, not only records
  metadata;
- device-resident internal phases inside RTDL-managed work;
- generic continuation families such as grouped reduction, component union,
  topology stream, threshold summary, ranked summary, and prepared graph chunk;
- explicit backend and explicit partner contracts;
- phase accounting that separates prepare, query, continuation, validation,
  and report overhead;
- no public performance claim without same-hardware pod evidence.

The target was not:

- C ABI;
- embedding;
- external host zero-copy interop;
- automatic backend or partner selection;
- app-specific native engines hidden behind benchmark names.

## 2. Optimization Inventory And Actual Effect

| Optimization / route | Category | Generic engine idea | Why we expected it to help | Current measured effect | Why it did not give V3-level performance |
| --- | --- | --- | --- | --- | --- |
| Fixed-radius prepared symbol/cache repair | `regression_repair` | Avoid repeated native symbol/library lookup in shared fixed-radius primitives | Barnes-Hut, Hausdorff, RTNN, RTDBSCAN all reuse fixed-radius or neighbor-style prepared queries; repeated lookup should be pure overhead | Same-pod focused 17-row packet: 1.062x geomean; OptiX subset 1.119x; grouped geomeans: Barnes-Hut 1.011x, Hausdorff 1.099x, RTDBSCAN 1.009x | Mostly repairs V3 overhead. It improves some rows, especially Hausdorff OptiX, but does not create broad all-app superiority. |
| Barnes-Hut prepared OptiX symbol/cache repair | `regression_repair` / `parity_recovery` | Prepared node-coverage threshold should avoid repeated lookup/setup | Serious run showed severe OptiX regressions, suggesting avoidable runtime overhead | Same-pod focused packet recovered old serious losses: 0.622x -> 0.999x, 0.591x -> 1.038x, 0.961x -> 0.990x. The 1.009x Barnes-Hut number is a post-hoc projection if the focused rows supersede the old serious rows, not a new full all-app run. | This is valuable regression repair, but parity recovery is not a major-version win. |
| RTNN prepared repeat50 amortization row | `hot_query_amortized_row_scoped` | Prepared ranked-summary repeated queries should reuse one search structure | Hot query can be fast if load/pack/prepare overhead is amortized and the usage contract is repeat-query | Reviewed row-scoped evidence: 7.889x hot-query, 1.315x cold-plus-query, 3.761x runner-wall over a CuPy uniform-grid CUDA-core reference across 50 prepared repeated queries | Useful scoped prepared-session evidence, but not one-shot RTNN, not full RTNN, not V3-vs-V2 broad proof. The three numbers must travel together. |
| RTNN prepared neighbor symbol/cache repair | `regression_repair_no_material_speedup` | Ranked-summary handles should not repeatedly resolve native symbols | If symbol lookup was material overhead, caching should improve stress-scale RTNN rows | Same-pod focused 12-row result: 1.001x geomean patched V3 vs V2.14; 1 row >5%, 11 within +/-5%, 0 slower >5% | The bottleneck is not symbol lookup. Setup, packing, contract shape, or summary path dominate. |
| Fixed-radius self-query device-search refresh | `contract_cleanup_no_speedup` | Avoid host query-point repack/upload for self-query paths | More device-resident fixed-radius graph work should reduce hidden host work | Three CuPy rows had about 0.998x after-vs-before geomean, with cleaner residency metadata | The route was already near the same bottleneck, or remaining overhead is elsewhere. It improves contract honesty, not speed. |
| Productized prepared execution/session runner M1-M1.2 | `runtime_surface_neutral` | Put fast paths behind a real runtime surface with backend, partner, cache, phase, and claim metadata | Row-level wins are not V3 unless users reach them through a shared runtime path | Runner was created and wired into grouped-stream and AABB routes. Early grouped-stream A/B was neutral at about 0.998x | First runner work improved visibility and contract discipline, but added a layer around already optimized paths. |
| AABB native query-handle runner M2.1 | `productized_path_win_row_scoped` | Reuse prepared native AABB query handles through the productized runner | Repeated AABB queries should benefit from handle reuse and phase split | Reviewed row-scoped evidence: 32,768 row cold-plus-collect 1.719x, query-total 1.867x; 65,536 row cold-plus-collect 1.637x, query-total 1.743x. Six fresh runs preserved weakest cold-plus-collect 1.644x. | This is the best current positive runner evidence, but it is one primitive family and exact row-scoped evidence, not broad V3 proof. |
| RTDBSCAN component-signature runner M3.1 | `runner_regression` | Productize component-union/component-signature work through the runner | Component union is a reusable continuation and should avoid row materialization | M3.1 failed: runner-vs-legacy geomean 0.504x; runner-vs-Embree 1.492x | The relevant incumbent is the legacy OptiX grouped-stream route, not Embree. Runner wrapper overhead dominated. |
| RTDBSCAN runner fingerprint/overhead fix M3.2 | `runner_parity_recovery` | Move expensive input fingerprinting out of the measured hot loop; use full SHA-256 sequence fingerprint instead of truncated repr | M3.1 timing showed native grouped work near legacy but wrapper overhead huge | M3.2 recovered runner-vs-legacy from 0.504x to 0.993x; runner-vs-Embree 2.934x | This is real generic overhead repair, but it recovered parity only. It is not a second material Set-A win. |
| RayDB grouped reduction device-column/scalar rows | `row_scoped_continuation` | Generic grouped continuation should avoid Python row materialization | Grouped count/sum are reusable continuation operations | RayDB app geomean 1.046x; some grouped rows positive | Evidence is row-scoped and not fully productized as a generic continuation runtime. |
| RTDBSCAN component-union/component-signature row | `row_scoped_continuation` | Generic compact component signature should replace host neighbor-row materialization | Component union can summarize connectivity without returning huge row lists | Serious app geomean 0.988x; focused runner parity after M3.2 | It is not full RTDBSCAN speedup and not yet a generic continuation family with material runner-backed win. |
| Triangle prepared graph chunk row | `row_scoped_prepared_graph` | Prepared graph/chunk execution should amortize setup and reduce repeated graph work | Triangle counting has chunkable repeated graph work | One exact 80,000-clique row is internal evidence; Triangle app geomean 0.987x | Prepared graph linkage is not production-grade or broad. One exact row does not prove the app or runtime. |
| Spatial topology stream row | `row_scoped_topology_stream` | Stream topology/point-location status instead of host relation loops | Spatial relation work should benefit from compact topology-stream output | Spatial app geomean 1.027x; some row-level signals | Public RayJoin/spatial performance remains blocked by scope, result-count, and paper-comparison issues. |
| Barnes-Hut fused Numba CUDA partner route | `row_scoped_explicit_partner` | Use explicit partner continuation for vector accumulation / aggregate frontier | RTDL may hand compact candidates to an explicit partner when partner work is the right continuation | Strong row-scoped partner evidence exists, but it is not an RT-core claim and not whole-app proof | Useful V3 partner-capability evidence, but not a broad RTDL runtime win unless generalized and reviewed. |

This accounting does not credit CUDA launch-configuration tuning, stream
concurrency, or allocator-policy work as completed Phoenix V3 performance
optimizations. No pod-backed Phoenix V3 accounting packet was identified for
those categories in the current handoff set. If such work exists elsewhere, it
must be added with the same evidence standard before being counted.

## 3. Why The Expectations Were Technically Reasonable

The original optimization ideas were not nonsense. They target real mechanisms:

- removing repeated symbol lookup and library loading should reduce pure
  runtime overhead;
- prepare-once/query-many should beat repeated prepare/query/report loops;
- typed continuations should reduce Python row materialization;
- device-resident internal phases should avoid host copies between RTDL phases;
- grouped summaries and component signatures should make large row outputs
  compact;
- explicit phase accounting should stop us from hiding cold/setup costs inside
  "fast" hot-query claims.

Those are legitimate language/runtime optimizations.

The problem is that most completed work either repaired regressions or proved
individual rows. It did not yet turn the reusable V3 execution layer into the
source of broad app-level speed.

## 4. Why The Actual Results Did Not Give Performance

### 4.1 Regression repair has a parity ceiling

Many fixes removed overhead introduced by V3 itself:

- repeated native symbol lookup;
- repeated cache-key construction;
- repeated report construction;
- unnecessary fingerprinting inside measured loops;
- avoidable wrapper/metadata cost.

These fixes are necessary. But their maximum result is usually:

```text
V3 stops being slower than V2.x.
```

That is not the same as:

```text
V3 is materially faster than V2.x.
```

M3.2 is the clearest example. It was a good fix:

```text
RTDBSCAN M3.1 runner_vs_legacy: 0.5038x
RTDBSCAN M3.2 runner_vs_legacy: 0.9930x
```

But the conclusion is parity recovery, not V3 success.

### 4.2 Hot-query speed was confused with user-visible speed

RTNN showed the trap clearly:

```text
prepared repeat50 row: 7.889x hot-query, 1.315x cold-plus-query,
3.761x runner-wall over the named CuPy uniform-grid reference
stress symbol-cache rerun: 1.001x geomean patched V3 vs V2.14 across 12 rows
```

Users experience wall time unless the language offers a real amortized prepared
session contract. A hot query that is fast after expensive pack/prepare work
does not prove the V3 runtime is broadly fast. The repeat50 row is useful
prepared-session evidence; the stress-scale V2.14 comparison shows that symbol
lookup caching alone does not move RTNN materially.

### 4.3 Row-scoped wins were not productized runtime wins

RayDB grouped reduction, RTDBSCAN component union, Triangle chunk execution,
Spatial topology stream, and Barnes-Hut partner continuation all contain useful
evidence. But V3 needs a runtime surface, not isolated benchmark routes.

The missing step is:

```text
shared execution path -> shared continuation contract -> repeated evidence
across multiple probes
```

Without that, the results are promising probes, not a language release.

### 4.4 The current all-app geomean mixes different workload classes

The 1.012x geomean is honest and should block release. But it also blends:

- residency/multi-phase workloads where V3 should win;
- single-shot/materializing controls where parity is the realistic target;
- row-level proof routes;
- app-level end-to-end routes;
- hot-query and cold-wall measurements.

This blend is useful as a harsh release blocker, but not sufficient for
engineering diagnosis. Before another all-app run, Set A and Set B must be
frozen:

- Set A: residency/multi-phase/continuation-rich probes where V3 must show
  material productized-path wins;
- Set B: single-shot/materializing controls where V3 must be at parity with
  clear explanation.

### 4.5 The runner became visible before it became cheap

The productized runner is architecturally necessary because it records:

- backend;
- partner;
- cache/reuse;
- phase timing;
- runtime execution;
- claim boundaries.

But a visible runner that adds overhead cannot be the performance story. AABB
M2.1 proves the runner can win. RTDBSCAN M3.1/M3.2 proves the runner is not yet
cheap enough or broad enough.

## 5. Current Positive Evidence That Still Matters

The honest positive evidence is narrow:

| Evidence | Why it matters | Why it is not enough |
| --- | --- | --- |
| Hausdorff app geomean 1.149x | Only app-level serious-run positive above 1.05x | One app does not make V3 a major release |
| AABB M2.1 runner-backed focused result | First material productized-path Set-A signal | One focused probe only; needs review and breadth |
| RTDBSCAN M3.2 parity recovery | Proves generic runner fingerprint/overhead fix worked | Parity is not material speedup |
| RayDB grouped rows | Shows grouped continuation can help | Not yet a productized generic continuation family |
| Barnes-Hut/RTNN hot or focused repairs | Shows some bottlenecks are identifiable | Mostly repairs or hot-query-only evidence |

The current material Set-A count is:

```text
material_set_a_runner_backed_probe_count: 1
first_material_probe: AABB M2.1
second_material_probe: missing
```

Therefore:

```text
full_all_app_rerun_authorized_now: false
release_authorized: false
```

## 6. Remaining Optimizations To Implement

These are the remaining optimizations worth doing because they are generic
language/runtime work, not app development.

### 6.1 Repeated prepared-session execution API

Expected implementation:

- one prepared task;
- one cache lookup;
- one prepared handle;
- warmup + measured repeats inside the runner;
- one report payload after the measured loop;
- no per-iteration fingerprint/report/task reconstruction.

Why we can expect an effect:

Legacy fast routes already use this shape manually. If the productized runner
matches the same shape, it can stop losing to legacy wrappers and can expose
real reuse as a V3 feature.

Required evidence:

```text
runner metadata present
runtime_executed: true
runner-vs-legacy >= 0.98x for repaired routes
runner-vs-legacy >= 1.15x for any material Set-A candidate
claim flags remain false
```

Failure mode:

```text
If the repeated runner still lands near 1.00x after per-iteration overhead is
removed, this path is parity repair only. Stop using it as a speed thesis and
move to typed continuation / residency work.
```

### 6.2 Productized typed continuation runner

Expected implementation:

- typed/device columns as input;
- generic grouped reduction and component-union contracts;
- compact device/column summaries as output where possible;
- no Python row materialization in the hot path;
- explicit partner only when partner continuation is chosen by the user or
  benchmark contract.

Why we can expect an effect:

The strongest row-scoped evidence repeatedly comes from the same pattern:

```text
RT traversal produces candidates -> typed continuation summarizes candidates
without materializing huge rows
```

Productizing that pattern is more likely to create V3 value than another
benchmark-specific native path.

Required evidence:

```text
same continuation contract used by at least two probes
material speedup on at least one Set-A route
parity or better on the second route
no app-specific native symbols
```

Failure mode:

```text
If typed continuations only win by changing one benchmark's semantics or adding
app-shaped native symbols, reject the result. If the shared contract reaches
only parity on all probes, keep it as cleanup but stop counting it as a material
V3 speed path.
```

### 6.3 Device-resident internal phase contract

Expected implementation:

- internal RTDL phases keep intermediate columns resident when the selected
  backend/partner supports it;
- host materialization happens only at final result or when the benchmark
  contract requires host rows;
- phase accounting reports each host boundary.

Why we can expect an effect:

Several failed or ambiguous results are explained by data movement, packing, or
materialization cost. If V3 cannot keep its own intermediate work resident, it
cannot beat V2.x on multi-phase workloads.

Required evidence:

```text
no hidden host materialization in hot phase
phase timing exposes prepare/query/continuation/finalize separately
Set-A route shows material speed from residency, not from benchmark cache tricks
```

Failure mode:

```text
If phase accounting shows the same host materialization or packing cost remains
between RTDL-owned phases, then V3 has not achieved the residency mechanism. Do
not continue performance claims until the host boundary is removed or explicitly
declared part of the contract.
```

### 6.4 AABB runner generalization

Expected implementation:

- generic runtime artifact: one shared AABB candidate-stream / range-
  intersection runner primitive using prepared native query-handle reuse;
- measurement probes: Contact Manifold-style and LibRTS-style AABB workloads
  exercise that same primitive without app-specific native symbols;
- keep the AABB M2.1 runner contract and phase accounting;
- reject any implementation that copies the route per app instead of sharing
  the primitive family.

Why we can expect an effect:

AABB M2.1 is the one current material productized-path result:

```text
32768 row cold-plus-collect speedup: 1.719x
32768 row query-total speedup: 1.867x
65536 row cold-plus-collect speedup: 1.637x
65536 row query-total speedup: 1.743x
six fresh runs weakest cold-plus-collect speedup: 1.644x
```

If the same mechanism works across multiple AABB probes, it becomes V3 engine
evidence rather than a single route.

Required evidence:

```text
same generic AABB primitive family
same runner contract
at least two probes measured
no app-specific AABB engine
```

Failure mode:

```text
If the additional AABB probes do not preserve material wall speed under the same
primitive contract, M2.1 remains a valid row-scoped result but not a generalized
V3 engine claim. Stop broadening AABB as a release pillar.
```

### 6.5 RTNN setup/packing amortization

Expected implementation:

- generic runtime artifact: amortized prepared-session mode for repeated
  ranked-summary style queries, with reusable prepared input packages and
  phase-stable report output;
- measurement probe: RTNN uses that generic artifact to test whether repeated
  query workloads can convert hot-query speed into wall-clock value;
- column residency across repeated ranked-summary queries;
- phase report separating load, pack, prepare, query, continuation, and final
  summary;
- no RTNN-specific native shortcut.

Why we can expect an effect:

RTNN has demonstrated hot-query upside, but cold/wall paths lose the benefit.
The only honest optimization is to either remove setup/packing cost or make
amortized usage a first-class V3 contract.

Required evidence:

```text
hot-query speed reported separately
cold-plus-query reported separately
runner-wall reported separately
amortized prepared-session mode documented and tested
```

Failure mode:

```text
If cold-plus-query and runner-wall remain near parity or slower while hot-query
stays fast, the bottleneck is not the reusable runtime wrapper alone. Stop
quoting RTNN as a V3 performance path unless setup/packing is removed by a
generic contract change.
```

### 6.6 Frozen Set A / Set B scorecard before another full pod run

This is not a speed optimization, but it is required to make speed claims
honest.

Expected implementation:

- preregister each benchmark row as Set A or Set B;
- Set A must show material productized-path wins;
- Set B must show parity with explanation;
- fail the release gate if classification is missing or changed after results.

Why we can expect an effect:

It prevents another ambiguous `1.0x` geomean from hiding both real wins and
real failures.

Required evidence:

```text
classification_frozen_before_run: true
all surprising rows explained
Set A and Set B reported separately
old blended geomean still reported as a harsh sanity check
```

Failure mode:

```text
If Set A / Set B classification changes after seeing results, the run is not
release evidence. If Set A does not show material productized-path wins, V3
remains redo_required even if the blended geomean looks less bad.
```

## 7. Work That Should Stop

The following should not be treated as a V3 performance strategy:

- more isolated app rows that do not enter the shared runner or continuation
  contracts;
- more symbol-cache-only work after a route reaches parity;
- hot-query-only claims without cold/wall/amortization disclosure;
- OptiX-vs-Embree claims when the decision-relevant comparison is V3 vs V2.x or
  runner vs incumbent legacy route;
- public RayJoin/spatial claims without result-count, scope, and paper-basis
  clarity;
- broad V3-over-V2 wording before fresh same-hardware evidence clears the
  release bar;
- any V4/C-ABI/embedding/SDK/host-zero-copy work inside Phoenix V3.

## 8. Next Concrete Sequence

The next responsible sequence is:

1. Close the current documentation/accounting record.
2. Get bounded external review of this accounting and the M3.2 classification.
3. Implement repeated prepared-session execution inside the runner.
4. Productize one typed continuation family used by at least two probes.
5. Re-run focused Set-A pod evidence only.
6. Freeze Set A / Set B.
7. Run a full same-hardware V2.14 vs Phoenix V3 comparison only after at least
   two material productized-path Set-A probes exist.

Stop rule:

```text
If two more productized-path Set-A attempts fail to produce material focused
evidence, stop Phoenix V3 performance work and hand off a redesign packet.
```

## 9. Sources

- `docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json`
- `docs/reports/phoenix_v3_optimization_effectiveness_and_remaining_plan_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md`
- `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`

## 10. Goal-Level Decision Audit

Decision: record Phoenix V3 as performance-failed for release while preserving
only the generic optimization paths that still have a plausible mechanism.

1. Was I foolish?
   No for this decision. It starts from the failed same-hardware evidence rather
   than from desired release language.
2. If yes, what actions made the decision foolish?
   The foolish actions would be to call parity "success," to count OptiX-vs-
   Embree where runner-vs-incumbent is the real comparison, or to treat
   regression repair as major-version performance.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. The alternative is to stop app-by-app patching and move only on
   productized runner execution, typed continuation, and residency contracts.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is repeated prepared-session execution plus productized
   typed continuation, followed by focused Set-A pod evidence before any
   broader run or claim.
