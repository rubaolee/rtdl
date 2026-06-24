# Phoenix V3 Optimization Effectiveness And Remaining Plan

Date: 2026-06-22
Status: `technical_accounting_not_release_authorization`

## Bottom Line

Phoenix V3 does not currently have broad performance proof.

The controlling same-RT-hardware V2.14 vs Phoenix V3 run completed cleanly, but
it did not clear the major-version performance bar:

```text
same_metric_comparison_count: 52
overall_geomean_v3_speedup_vs_v2_14: 1.0117790403434224
apps_with_geomean_gt_1_05: 1
apps_with_geomean_lt_0_95: 2
release_consideration_eligible: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

App-level geomeans:

| App | V3 vs V2.14 app geomean | Current reading |
| --- | ---: | --- |
| `hausdorff_xhd` | 1.149x | strongest app-level positive result |
| `raydb_style` | 1.046x | modest, below major-version evidence |
| `spatial_rayjoin` | 1.027x | row-level signals, no app win |
| `contact_manifold` | 1.017x | near parity |
| `rtnn` | 1.003x | parity |
| `robot_collision` | 0.993x | parity/slight loss |
| `rt_dbscan` | 0.988x | slight loss |
| `triangle_counting` | 0.987x | slight loss |
| `librts_spatial_index` | 0.937x | regression |
| `barnes_hut` | 0.844x | regression in the serious run, later focused repair evidence exists |

The honest current statement is:

```text
Phoenix V3 has useful reusable-engine evidence and several focused fixes, but
it is not yet a user-responsible major performance release.
```

## Why This Document Exists

The project has done real optimization work, but the work splits into four
very different categories:

1. row-scoped capability wins that do not generalize to app-level V3 proof;
2. regression repairs that recover V3 back toward V2 parity;
3. productized runner work that improves architecture visibility but is not
   yet consistently faster;
4. one material focused Set-A runner-backed win, AABB M2.1, that is still only
   one probe.

This document records what was attempted, why it was expected to help, what
actually happened, and what remains worth doing.

## Optimization Inventory

| Optimization / route | Why we expected it to help | Actual effect | Why it did not become broad V3 performance |
| --- | --- | --- | --- |
| RayDB grouped reduction device-column/scalar-broadcast rows | Grouped reductions are a generic continuation pattern; device columns should avoid Python row materialization and repeated host work. | Three grouped-reduction rows are retained as reusable internal engine evidence. RayDB app geomean in the serious run is 1.046x. | The wins are row-scoped and not routed through the current productized execution path. They prove `grouped_reduction`, not a database product or broad V3-over-V2 speedup. |
| RTDBSCAN component-union / component-signature row | Component union is a reusable continuation; removing point-id/core-flag materialization should reduce continuation overhead. | One row-scoped `component_union` capability is retained. Earlier optimized evidence showed OptiX-vs-Embree row speedups around 1.10x-1.24x. Serious app geomean is 0.988x. | It is not full RTDBSCAN, not paper reproduction, and not productized runner proof. The M3.1 runner-backed A/B later showed the runner path at only 0.504x vs the incumbent legacy OptiX path. |
| Triangle prepared graph chunk row | A prepared graph/chunk execution shape should amortize graph setup and avoid repeated graph stream work. | One exact 80,000-clique non-graph-stream row is M7-qualified internally. Triangle app geomean in the serious run is 0.987x. | The prepared-graph executor linkage is not broadly closed. One exact row does not prove full Triangle app speed or broad V3 runtime superiority. |
| Spatial topology stream row | A point-location topology stream with guarded boundary handling should reduce relation-status work. | One internal `point_location_topology_stream` row is retained. It has a default-path speedup vs an author query timer, but Spatial app geomean is 1.027x. | Result-count/paper-scope proof and public RayJoin wording remain blocked. The row is useful internal topology-stream evidence, not public Spatial speedup. |
| RTNN ranked-summary hot query | Prepared OptiX hot queries should beat same-contract CUDA-core reference when setup is amortized. | 1,048,576-point run showed 7.790x hot-query speedup, but only 0.393x cold-plus-query and 0.627x runner-wall. Later symbol-cache focused run was 1.001x geomean. | Pack/load/prepare dominate end-to-end. Hot query alone is not user-visible app speed unless V3 amortizes or removes setup overhead. |
| Barnes-Hut prepared OptiX symbol/cache repair | Serious run regressions looked like repeated runtime/symbol lookup overhead, not algorithmic failure. | Largest OptiX losses recovered from 0.622x/0.591x to 0.999x/1.038x. Estimated Barnes-Hut app geomean improved from 0.844x to 1.009x in the focused repair context. | This is important regression repair, but it mostly moves V3 from bad to parity. Regression repair cannot by itself create a major-version performance story. |
| LibRTS AABB count packing/symbol cache | Repeated AABB query packing and native symbol lookup should be avoidable through prepared-query reuse. | Embree count-only regression was recovered in focused runs; OptiX AABB row remains unstable/inconclusive. | It fixes part of one generic AABB path, but not all backends and not enough all-app breadth. AABB single-shot/control rows also have limited upside. |
| Fixed-radius symbol/library cache | Fixed-radius prepared count-threshold is shared by Hausdorff, RTDBSCAN, and Barnes-Hut, so symbol/cache repair should help multiple probes. | Focused 17-row packet: 1.062x geomean V3 vs V2.14; OptiX subset 1.119x. Hausdorff benefits materially in several cases. | The gain is concentrated, mainly Hausdorff/OptiX. It is useful generic cleanup, but not enough to rerun or release the whole suite. |
| Fixed-radius self-query device-search refresh | Avoiding host query-point repack/upload should improve device residency and reduce hidden host work. | Three successful CuPy rows had 0.998x after-vs-before geomean with improved residency metadata. | The old route was already close to the same bottleneck, or the remaining overhead is elsewhere. This is contract cleanup, not speed. |
| Prepared execution/session runner M1-M1.2 | A real productized runner should expose backend/partner, cache, phase accounting, residency, and claim boundaries in one reusable runtime path. | M1/M1.1/M1.2 created and wired the runner. Grouped-stream route A/B was neutral at 0.9979x. | The first route proved visibility, not speed. It added a runner layer around an already optimized path. |
| AABB runner M2.1 | AABB native query handles should benefit from explicit prepared-session reuse across repeated queries. | First material focused Set-A runner-backed evidence: OptiX/Embree cold-plus-collect 1.346x, query-total 1.738x, runner-wall 1.337x. | This is real positive focused evidence, but it is only one Set-A probe and does not authorize release or all-app rerun by itself. |
| RTDBSCAN runner M3.1 | The runner should productize component-signature execution without changing the reusable route. | Valid negative evidence: runner metadata present, signatures stable, but geomean runner-vs-legacy is 0.504x. Runner-vs-Embree is 1.492x, but that is not the relevant incumbent. | The bottom native work is similar to legacy; the wrapper adds repeated Python-side fingerprint/cache/report/metadata overhead inside the measured loop. |

## Why The Expectations Were Reasonable

The original V3 expectations were not technically absurd. They targeted real
performance mechanisms:

- prepared scenes and handles should amortize setup;
- fixed-radius self-query should avoid host query repack/upload;
- grouped reductions and component unions should avoid Python row materialization;
- topology streams should replace host relation-status loops;
- prepared hot queries should win when setup is amortized;
- a productized execution/session runner should prevent fast paths from living
  only as benchmark-app routes.

Those are valid runtime/language goals.

The mistake was not the direction. The mistake was over-reading partial,
row-scoped, or hot-query evidence as if it proved a major V3 release.

## Why The Actual Results Did Not Meet The V3 Bar

### 1. Too much work was regression repair

Symbol/cache fixes in Barnes-Hut, RTNN, LibRTS, and fixed-radius paths were
necessary, but their ceiling is mostly parity. They remove V3 overhead that V2
did not pay. Claude's review called this out correctly: regression chasing can
asymptote to 1.0x but cannot create material superiority.

### 2. Row-scoped wins were not productized runtime wins

RayDB grouped reduction, RTDBSCAN component union, Triangle prepared graph, and
Spatial topology stream are real internal capability evidence. But a row is not
a user-facing language/runtime improvement unless the user can reach it through
a coherent runtime surface and it affects enough meaningful workloads.

### 3. Hot-query wins were hidden by cold/setup/packing cost

RTNN is the clearest example. A 7.790x hot-query win exists, but cold-plus-query
is 0.393x and runner-wall is 0.627x. Users experience wall time unless V3
explicitly supports amortized prepared sessions and makes that usage clear.

### 4. The productized runner is architecturally right but not yet cheap enough

AABB M2.1 proves the runner can be a source of real win. RTDBSCAN M3.1 proves
the current runner shape can also be too expensive.

In RTDBSCAN M3.1, representative timing shows the native grouped operation is
not slower:

```text
65,536 legacy grouped_native_sec: 0.090146
65,536 runner grouped_native_sec: 0.089911
65,536 runner adapter_non_native_estimated_sec: 0.153663

262,144 legacy grouped_native_sec: 1.246784
262,144 runner grouped_native_sec: 1.247843
262,144 runner adapter_non_native_estimated_sec: 0.633671
```

The loss is wrapper overhead: repeated large input fingerprinting, cache-key
work, report construction, and metadata validation inside the measured loop.
Claude's external review also identifies the current large-sequence fingerprint
as a correctness risk because it uses truncated sequence reprs as cache-key
material. The next runner fix must address both performance and cache-key
correctness.

M3.2 local update: `make_prepared_input_fingerprint` now uses a full streaming
SHA-256 digest for large sequences, and the RTDBSCAN runner route precomputes
that fingerprint outside the measured loop. This is local contract/correctness
work only until a focused pod A/B measures it.

M3.2 pod update: the focused A/B recovered RTDBSCAN runner-vs-legacy from
`0.5038x` to `0.9930x` geomean. That validates the generic overhead fix as
parity recovery, but it is not a material Set-A win because it is not faster
than the incumbent legacy OptiX route.

### 5. The blended all-app geomean mixes different workload classes

Some apps are residency/multi-phase probes where V3 can win. Others are
single-shot or materializing controls where parity is the realistic target.
The current 1.012x geomean is honest, but it is also a blunt instrument. It
does prove "not release-ready"; it does not tell us which architectural work is
worth continuing unless we split Set A and Set B before the next all-app run.

## Current Technical Classification

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_now: false
material_set_a_runner_backed_probe_count: 1
first_material_probe: AABB M2.1
second_material_probe: missing
current_p0: productized prepared execution/session runner overhead and breadth
```

## Remaining Optimizations Worth Implementing

### 1. Generic runner overhead fast path

Implement a runner mode that does not recompute large input fingerprints and
full report metadata on every measured iteration.

Expected mechanism:

- precompute stable input fingerprints outside the hot loop;
- allow helpers to pass an explicit prepared-session key or input fingerprint;
- replace truncated sequence repr cache-key material with a collision-resistant
  bounded hash or caller-supplied stable fingerprint;
- separate "prepare/report once" from "run prepared N times";
- keep the same release/public/claim flags false;
- preserve explicit backend, partner, cache, residency, and phase accounting.

Why this should help:

RTDBSCAN M3.1 shows native work is already near legacy parity while wrapper
overhead is large. Removing runner overhead can recover the route toward the
legacy OptiX path without adding RTDBSCAN-specific engine logic.

Success evidence required:

```text
RTDBSCAN runner-vs-legacy >= 0.98x minimum
RTDBSCAN runner-vs-legacy >= 1.15x preferred only if overhead removal exposes a real win
runner metadata still present
signatures stable
claim flags false
```

### 2. Repeated prepared-session execution API

Add a productized repeated-run wrapper that takes one prepared task and executes
warmup + measured repeats inside the runner, returning per-repeat timings.

Expected mechanism:

- one cache lookup;
- one prepared handle;
- N measured executions;
- one report payload summarizing cold, cache, warmup, measured median, and
  validation;
- no repeated task object/fingerprint/report construction per iteration.

Why this should help:

The legacy fast paths use exactly this shape: prepare once, loop many times.
The runner must match that shape before it can fairly replace legacy routes.

### 3. Productize grouped continuation over typed/device columns

Move grouped reduction / component union into a shared continuation runner
rather than keeping them as RayDB or RTDBSCAN shaped rows.

Expected mechanism:

- typed input columns;
- explicit partner;
- output stays as compact device/column summaries;
- no Python row materialization in the hot path;
- one continuation contract usable by RayDB grouped reduction, RTDBSCAN
  component union, and potentially Triangle-style chunk summaries.

Why this should help:

This is the common mechanism behind the strongest row-scoped M0-M149 evidence.
It is more likely to create V3 language/runtime value than another app-specific
benchmark route.

### 4. AABB runner generalization across AABB users

Keep AABB M2.1 as first material focused evidence, then verify whether the
same prepared native query-handle runner benefits both Contact Manifold and
LibRTS-style AABB workloads under the same contract.

Expected mechanism:

- prepared AABB index;
- native query-handle reuse;
- explicit row capacity for OptiX;
- phase accounting for prepare, query, collect, and runner overhead.

Why this should help:

AABB M2.1 already cleared a material focused bar. The remaining question is
whether that win is route-specific or a reusable AABB primitive family.

### 5. RTNN setup/packing amortization

Do not chase RTNN symbol lookup further. Attack the gap between hot-query
speed and wall time.

Expected mechanism:

- reusable prepared input package;
- column residency across repeated ranked-summary queries;
- explicit amortized-prepared usage mode;
- phase report that separates load/pack/prepare/query.

Why this should help:

RTNN has a large hot-query signal but bad cold wall time. The only honest path
to user-visible value is to either amortize setup in the contract or reduce it
directly.

### 6. Freeze Set A / Set B before another all-app run

This is not an optimization, but it is required before performance work can be
interpreted responsibly.

Expected mechanism:

- Set A: residency/multi-phase/continuation-rich probes where V3 should win;
- Set B: single-shot/materializing/ceiling controls where V3 should be near
  parity with explanation;
- classification frozen before the run;
- all surprising rows explained.

Why this should help:

It prevents another ambiguous 1.0x blended geomean from hiding both useful
wins and real failures.

## Work That Should Not Continue As A V3 Strategy

- More isolated app rows that do not enter a shared runner or continuation
  primitive.
- More symbol-cache-only work after current regressions are repaired to parity.
- Public Spatial/RayJoin speedup wording without result-count and paper-scope
  proof.
- Hot-query-only claims without cold/wall/amortization disclosure.
- Full all-app rerun before at least two material productized-path Set-A probes
  exist and Set A / Set B classification is frozen.
- Any C ABI, embedding, SDK, or multi-language host work in V3.

## Recommended Next Order

1. Implement the generic repeated prepared-session runner / precomputed
   fingerprint fast path. Initial M3.2 local fingerprint work is complete;
   repeated prepared-session execution is still open.
2. Re-run the RTDBSCAN M3.1/M3.2 focused pod A/B. Done: parity recovered, not
   material.
3. Either implement repeated prepared-session execution to seek real runner
   speed, or switch to another Set-A route.
4. Seek one bounded external review of the new evidence.
5. Freeze Set A / Set B.
6. Only then consider a new serious all-app V2.14 vs Phoenix V3 run.

## Goal-Level Decision Audit

Decision: record Phoenix V3 optimization effectiveness as mixed and currently
insufficient for release, while preserving the remaining generic optimization
path.

1. Was I foolish?
   No for this decision.
2. What actions would have made this foolish?
   It would be foolish to describe the work as either "nothing worked" or "V3
   is successful." The evidence shows useful optimization pieces, but not broad
   performance.
3. Was there another path?
   Yes. I could continue coding without this accounting, but that would leave
   the project unable to decide which pod time is justified.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is to optimize the productized runner overhead and
   require focused pod evidence before any broader claim.
