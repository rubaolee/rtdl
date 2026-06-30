# RTDL v2.14 App-Author Implementation Strategy

Status: v2.14 user-facing design guidance for app authors. This is not a
release tag, automatic optimizer promise, whole-app speedup claim, or raw OptiX
callback API proposal.

Use this document when you want to implement a new program with RTDL and need
to decide:

- which RTDL primitive to start from;
- whether to use OptiX/RT cores, Embree CPU, or both;
- whether custom continuation should be a partner path;
- when a missing operation should become a new generic RTDL primitive;
- why v2.14 does not expose arbitrary OptiX callback functions as a stable user
  API.

## One-Sentence Rule

Start primitive-first, make partner continuation explicit, keep backend
comparisons same-contract, and treat raw OptiX-style callbacks as native
implementation details behind generic RTDL primitives rather than as the normal
user extension surface.

## Decision Tree

| Question | Preferred v2.14 answer |
| --- | --- |
| Can an RTDL primitive directly express the answer? | Use the primitive and stop there. |
| Does the app need only compact flags, counts, summaries, or bounded witnesses? | Use a compact-output primitive. |
| Does the app need repeated queries over the same geometry? | Use a prepared primitive/session and report hot-query and cold-total timing separately. |
| Does the remaining work require app-specific labels, topology, convergence, force accumulation, or refinement? | Use an explicit partner continuation after the primitive. |
| Does a public claim depend on partner continuation? | Measure the current best partner and a same-contract Numba reference. |
| Does the app need a custom closest-hit, any-hit, or intersection behavior? | Prefer a new app-agnostic primitive. Do not expose arbitrary user callbacks as a v2.14 stable API. |
| Do OptiX and Embree routes differ in contract, partner, output, or timing basis? | Do not compare them as backend-only evidence. |

## Step 1: Find The RT-Shaped Kernel

Most applications are not "one ray tracing program." They are a pipeline with
one or more RT-shaped kernels inside it. First isolate those kernels.

| App need | RTDL primitive family to look for first |
| --- | --- |
| Spatial index, broadphase, range query | Prepared AABB index / AABB query primitives |
| Boolean collision, visibility, candidate existence | Any-hit flags or scalar any-hit summaries |
| Segment, triangle, ray, or shape-pair counting | Prepared scalar count or weighted any-hit summary |
| Grouped SQL/RayDB-style aggregation | Native grouped reductions: count, sum, min, max, or i64 reductions |
| Radius-neighborhood threshold decisions | Fixed-radius count-threshold primitives |
| Ranked or nearest-neighbor summaries | Fixed-radius ranked-summary aggregates |
| Candidate/witness extraction | Bounded collect primitives |
| Point-in-polygon or line-segment-intersection scalar answers | Prepared RayJoin-style scalar-count primitives |

If one of these primitives returns the final answer, do not add a partner just
because a GPU array library is available. Extra partner work can add launches,
copies, synchronization, and materialization.

## Step 2: Choose Backend As A Deployment And Evidence Decision

RTDL v2.14 supports two major production comparison lanes:

- RTDL OptiX for NVIDIA GPUs / RT cores.
- RTDL Embree for CPU cores.

Choose both when you need a serious "buy NVIDIA RT cores or run on multicore
CPU" comparison. Choose one when your deployment environment is fixed.

| Situation | OptiX/RT-core route | Embree CPU route |
| --- | --- | --- |
| Large traversal-heavy workload with compact output | Usually the main candidate | Fair CPU baseline |
| Small or one-shot workload | May be dominated by setup and transfer | Often competitive |
| Repeated queries over a prepared scene | Strong fit | Also report hot/cold split |
| Output-heavy workload that materializes many rows | Speedup may shrink | Often closer than expected |
| CPU-only deployment | Not applicable | Main route |
| User needs architecture comparison | Required | Required |

The comparison rule is strict: OptiX-vs-Embree claims must use the same app row,
same primitive contract, same output surface, same partner policy, same data,
and a clear timing protocol.

## Step 3: Use Prepared Execution When Reuse Exists

Prepared execution is the default pattern for serious v2.14 performance work:

```text
load or generate app data
prepare RTDL scene/index once
run repeated queries against the prepared object
emit compact output
optionally run explicit partner continuation
report prepare/cold total and hot-query timing separately
```

Do not hide scene build inside a hot-query number. Do not compare a cold OptiX
number against a hot Embree number, or vice versa.

## Step 4: Add Partner Continuation Only For App-Specific Work

A partner is the app-owned continuation after RTDL emits a generic output:
flags, counts, summaries, bounded witnesses, typed columns, or candidate rows.

| App pattern | Primitive contribution | Partner contribution | Boundary note |
| --- | --- | --- | --- |
| RTDBSCAN | Fixed-radius count threshold / core flags | Component labeling or convergence | For OptiX-vs-Embree backend comparison, fix Numba as the continuation lock; for partner comparison, current large-scale evidence shows Numba as the measured 524K winner over same-contract CuPy. |
| RayJoin overlay | LSI, point-location, PIP, bounded counts | Topology and output assembly | Overlay claims are limited to the available 2/8 exact Section 5.7 CDB subset; full 8/8 reproduction is blocked. |
| Barnes-Hut | Node coverage / threshold frontier | Force-vector accumulation | v2.14 reports node coverage only, not full force-solver acceleration. |
| Contact manifold | AABB broadphase / witness candidates | Exact contact refinement | v2.14 reports broadphase/contact-witness evidence, not full physics-engine contact generation. |
| Hausdorff exact witness | Threshold decision or frontier | Exact nearest-witness continuation | v2.14 reports threshold decision only, not exact witness-distance acceleration. |
| Triangle candidate interpretation | Scalar any-hit/count summary | Candidate compaction and app-owned interpretation | v2.14 scalar answer is primitive-first; candidate-row interpretation is a separate app-owned continuation. |

Partners are not hidden backend selection. The app chooses them explicitly and
the report must name them.

## Step 5: Choose A Partner

| Partner | Choose when | Notes |
| --- | --- | --- |
| Numba | You need Python-source custom kernels, no CUDA C++ build, loops, union-find, label propagation, component labeling, segmented reductions, or block reductions. | Required as the accessibility/reference path for partner-dependent claims. It can also win on some measured contracts. |
| CuPy | Your continuation is naturally expressed as device-array operations, scans, masks, reductions, RawKernel experiments, or CUDA graph replay around array work. | Often strong for dense CUDA-core baselines, but not automatically better than Numba. |
| Torch | Your data already lives in Torch tensors or the app is ML-pipeline-native. | Treat as an explicit partner, not an automatic RTDL route. |
| NumPy / CPU / Shapely / GEOS | You need correctness or exact topology or a small-scale oracle. | Usually not a GPU performance partner. |
| C++ / CUDA / specialized OptiX | You need expert-level fused hot compute or paper-code parity. | Valid as an external specialized baseline, but not the default RTDL language strategy. Do not use this path to claim RTDL primitive performance exceeds a specialized implementation. |

For any public partner-dependent claim, v2.14 requires:

1. a fixed primitive output contract;
2. the current best-performance partner for that contract;
3. a same-contract Numba reference;
4. the same data, repeat protocol, validation oracle, and timing breakdown;
5. explicit wording that partner choice is not automatic.

## Step 6: Compose Complex Apps As Pipelines

Complex programs should be written as explicit pipelines:

```text
prepared primitive A
-> compact output
-> optional partner continuation
-> prepared primitive B
-> bounded collect or grouped reduction
-> app-owned policy and final output
```

This is the v2.14 way to express app strategy. Examples:

- RayJoin overlay combines LSI, vertex/midpoint point-location, PIP traversal,
  and output orchestration.
- RTDBSCAN combines RT fixed-radius threshold columns with Numba prepared-grid
  component continuation.
- Contact manifold combines AABB broadphase with bounded witness rows and
  app-owned exact refinement.

The key boundary is that app policy belongs in the app or partner, while the
native RTDL engine remains app-agnostic.

## Step 7: When To Request A New Primitive

Request or design a new RTDL primitive when the missing behavior is generic
enough to serve more than one app.

Good primitive candidates:

- closest-hit id or face-id query;
- filtered any-hit count;
- bounded candidate collect;
- grouped aggregate;
- fixed-radius threshold columns;
- ranked summary;
- compact witness rows;
- generic point-location or containment primitive with a clear output contract.

Bad primitive candidates:

- "RayJoin overlay output assembly exactly as this benchmark wants it";
- "DBSCAN labels with this app's private convergence policy";
- "Barnes-Hut force law with this app's timestep assumptions";
- "Contact manifold generation for this one physics engine";
- arbitrary user-provided CUDA or OptiX callback with no Embree contract.

## Why v2.14 Does Not Expose Raw OptiX Callback APIs

OptiX has raygen, miss, closest-hit, any-hit, and intersection programs. RTDL
uses OptiX internally where appropriate, but v2.14 does not expose arbitrary
user callback functions as the normal stable user API.

Reasons:

1. Arbitrary callbacks break the OptiX/Embree same-contract comparison unless
   an equivalent CPU contract exists.
2. Callback ABI, device memory ownership, compilation, stream semantics, and
   synchronization are hard to make safe as a language-level surface.
3. Direct callbacks push users back toward one-off C++/CUDA/OptiX systems,
   which is exactly what RTDL is trying to avoid for common RT-shaped work.
4. Benchmark claims become ambiguous: the speedup may belong to app-specific
   expert code rather than to a reusable RTDL primitive.

The preferred v2.14 pattern is:

```text
custom OptiX program internally implements a generic RTDL primitive
generic RTDL primitive exposes a stable app-agnostic contract
apps compose primitives and partners explicitly
```

Specialized C++/CUDA/OptiX remains valid as an external baseline or expert
implementation, but it should not be confused with the RTDL user strategy.

## Public Wording Template

Allowed:

```text
This app uses RTDL OptiX for the prepared fixed-radius threshold primitive and
Numba for explicit component-continuation under the named contract. The same
contract is also measured on RTDL Embree CPU.
```

Blocked:

```text
RTDL automatically chooses the best partner.
RTDL accelerates arbitrary Numba or CuPy programs.
RTDL exposes arbitrary OptiX callbacks as the user programming model.
RTDL proves whole-app speedups when only a primitive row was measured.
```

## v2.14 Benchmark Lessons

Status scope:

- RTDBSCAN is a narrow engineering row: the backend comparison fixes Numba as
  the shared continuation, and the 524K total speedup is small because
  continuation dominates.
- RayJoin PIP is a modest scalar-count row, not a broad RT-core win.
- RayJoin overlay is public-review-ready only for the available 2/8 exact CDB
  subset, not a full 8/8 Section 5.7 reproduction.

| Benchmark family | User lesson |
| --- | --- |
| RTNN | Native ranked-summary aggregate is a strong primitive-first pattern; keep exact and best float32 paths separate. |
| RTDBSCAN | RT threshold helps, but at 524K the continuation phase is about 6.9s and the RT threshold stage is about 1.2s of an 8.9s total; public wording must stay narrow, and Numba is currently the best measured prepared-grid partner for this contract. |
| RayJoin LSI | Scalar count is a strong primitive-first row. |
| RayJoin PIP | Current scalar count is modest; do not overclaim. |
| RayJoin overlay | The available 2/8 exact Section 5.7 subset is public-review-ready, but full 8/8 reproduction remains blocked. |
| RayDB-style | Use fused grouped reductions when they exactly answer the query. |
| LibRTS AABB | Prepared AABB index is a strong RTDL spatial-index pattern. |
| Triangle counting | Any-hit hot query can be excellent, but graph lowering and prepare affect total time. |
| Barnes-Hut | Node coverage is accelerated; full force solver needs explicit continuation. |
| Hausdorff/X-HD | Threshold decision is a primitive row; exact witness distance is a different app. |
| Robot collision | Grouped any-hit flags are a clean traversal primitive; full planning is out of scope. |
| Contact manifold | Broadphase can benefit; exact manifold refinement remains app-owned. |

## Final Checklist For App Authors

Before claiming performance, write down:

- the app row;
- the primitive contract;
- the backend or backend pair;
- the partner, if any;
- the fixed partner used for backend comparison, if any;
- the data scale and source;
- whether timing is cold total, hot query, or both;
- whether output is compact or materialized rows;
- the correctness oracle;
- the phase explanation;
- the blocked overclaims.

If any of those are missing, call the route experimental or compatible, not
performance-ready.

## See Also

- [Primitive Discovery Workflow](primitive_discovery_workflow.md)
- [Prepared Execution Pattern](prepared_execution_pattern.md)
- [Prepared Session Reuse](prepared_session_reuse.md)
- [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
- [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)
- [v2.14 Public RT-vs-Embree Comparison](../release_reports/v2_14/public_rt_vs_embree_comparison.md)
- [v2.14 Public Wording Boundaries](../release_reports/v2_14/public_wording_boundaries.md)
- Historical partner-evidence supplements are archived under the top-level
  [history](../../history/README.md) directory.
