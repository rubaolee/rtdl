# RTDL V3.0 App-Author Implementation Strategy

Status: V3.0 post-closure guidance for app authors after Goal4542 and
Goal4543. This is not a release tag, public performance claim, automatic
optimizer promise, raw OptiX callback API proposal, or proof that every app is
a broad RT-core speedup.

Use this document when you want to implement a program with RTDL and decide:

- which primitive family to start from;
- whether to use OptiX, Embree, CPU/Numba, Numba CUDA, or a mixed route;
- whether custom logic belongs in a partner continuation;
- when a missing operation should become a new app-agnostic RTDL primitive;
- how to compare RTDL with specialized C++/CUDA/OptiX or Embree code honestly.

## Current V3 State

Goal4542 records the current implementation surface:

- all ten benchmark apps are closed current targets;
- the runtime, claim/evidence, design-blocker, and future-design queues are
  empty;
- no current target requires immediate pod execution after Goal4543;
- release, public speedup, broad RT-core, paper-reproduction, automatic
  partner-selection, true-zero-copy, RTDL-beats-specialized-code, and
  app-specific native-engine claims remain blocked unless a later reviewed
  packet authorizes them.

## One-Sentence Rule

Start with the smallest app-agnostic primitive that returns useful compact
state, keep partner continuation explicit, choose routes by measured contract,
and create a new generic primitive when the missing operation is reusable
engine logic rather than app policy.

## Decision Tree

| Question | V3 answer |
| --- | --- |
| Can a current primitive return the final compact answer? | Use it directly and avoid a partner. |
| Does the app need repeated queries over stable geometry or indices? | Use prepared execution and report prepare, cold-total, and hot-query timing separately. |
| Does the app need labels, topology, force accumulation, convergence, row assembly, or exact geometry refinement? | Use an explicit partner continuation or app-owned CPU continuation after RTDL output. |
| Is the continuation naturally dense device-array work? | Try CuPy and Numba where the contract matters; choose by measured same-contract timing. |
| Is no-C++ accessibility required? | Keep Numba as the Python-source reference or implementation lane. |
| Is C++/CUDA/OptiX specialized code needed for a paper baseline? | Treat it as an external specialized baseline, not as evidence that RTDL itself is faster. |
| Does a missing operation require custom closest-hit, any-hit, or traversal semantics? | Prefer a reviewed app-agnostic primitive. Do not expose arbitrary raw callbacks as the stable user API. |
| Are OptiX and Embree being compared? | Keep data, output contract, partner policy, and timing basis identical. |

## Route Classes

| Route class | Use when | Current examples |
| --- | --- | --- |
| Primitive-first | RTDL returns the scalar, flag, count, bounded witness, or grouped summary the app needs. | Hausdorff/X-HD threshold, RayDB-style grouped reductions, LibRTS AABB query slices. |
| No-partner prepared primitive | The app is mostly repeated traversal with compact outputs. | Robot collision grouped-segment any-hit, contact-manifold bounded witnesses. |
| Mixed explicit | More than one route is valid and the user must choose by deployment, output, or scale. | Spatial RayJoin, RT-DBSCAN, Barnes-Hut, RTNN. |
| Partner continuation | RTDL emits generic device or host columns and app logic finishes the answer. | RT-DBSCAN component summaries, RTNN ranked-summary bridge, Triangle Counting segment replay. |
| Future primitive candidate | The hot continuation is generic enough that keeping it as app code causes avoidable movement or materialization. | Barnes-Hut RT-native hierarchical traversal, future graph-compatible weighted replay. |

## Current Benchmark Route Matrix

| App | Current route | Partner guidance | Boundary |
| --- | --- | --- | --- |
| Hausdorff / X-HD | Primitive-first exact nearest-witness / grouped-max route. | No partner for the promoted compact route. | M113 is not current path; public speedup wording remains blocked. |
| Spatial RayJoin | Mixed explicit: Numba for bounded PIP one-shot, prepared RTDL/OptiX for repeated PIP, scalar/active-count primitives for LSI and overlay. | Numba for bounded PIP continuation; no partner for scalar/active-count primitive rows. | Full RayJoin paper and Section 5.7 8/8 wording remain future optional claim expansion. |
| RT-DBSCAN | Fixed-radius count-threshold device columns plus explicit predicate direct-status compact-signature continuation. | CuPy is the measured compact-signature route; grouped-stream Numba remains fallback/reference. | Full rows are a different output contract; automatic route selection remains blocked. |
| Robot collision | Prepared grouped-segment any-hit with NumPy query lowering. | No promoted partner needed. | Planner/exact-solid collision wording is outside the primitive claim. |
| Contact manifold | Prepared bounded contact-witness collect. | No promoted partner needed. | No manifold-native ABI or full physics contact-generation claim. |
| RayDB-style | Primitive-first grouped count/sum/min/max/i64 reductions. | Partner rows only for unfused continuations. | Do not force a partner when the primitive already returns the fused scalar/summary. |
| Barnes-Hut | Mixed explicit by scale: fused CPU/Numba for tested 8192/16384/32768 rows, fused Numba CUDA for tested 65536/131072 rows, prepared RTDL/OptiX+Numba only as OptiX-library CUDA device-column evidence. | Numba is the current no-C++ CPU/GPU fused lane; CuPy remains comparison for the prepared aggregate-frontier contract. | Goal4541 closes current route classification only; RT-native hierarchical traversal is not implemented and no Barnes-Hut RT-core speedup claim is authorized. |
| LibRTS spatial index | Prepared AABB index query slice. | No promoted partner needed. | This is not a full mutable LibRTS replacement. |
| RTNN | Mixed explicit: exact float64 aggregate for same-contract OptiX-vs-Embree comparison, full-batch non-graph prepared aggregate for KITTI-family aggregate-only rows, and prepared graph plus CuPy/Numba same-stream bridge for resident app evidence. | CuPy/Numba both matter for same-stream partner bridge; route choice is explicit. | Exact paper reproduction and same-output author wording remain future optional claim expansion. |
| Triangle counting | Current internal route is prepared segment replay with `numba_direct_sort_rle`; scalar answer remains primitive-first. | CuPy and Numba paths are explicit route choices around segment construction and replay. | cuGraph/authors kernels remain separate baselines; M113 graph readiness and public RT-core speedup wording remain blocked. |

## Backend Choice

RTDL V3 uses backend choice as an evidence and deployment decision, not as a
magic speedup switch.

| Situation | Preferred action |
| --- | --- |
| NVIDIA deployment and traversal-heavy compact output | Start with OptiX/prepared RTDL primitive. |
| CPU deployment or fair CPU baseline | Use Embree or CPU/Numba under the same output contract. |
| Output-heavy or materialization-heavy workload | Expect RT-core advantage to shrink; optimize output contract first. |
| App-specific dense continuation | Use CuPy or Numba explicitly and report partner timing separately. |
| No-C++ user workflow | Prefer Numba, prepared RTDL primitives, and Python-owned policy. |
| Specialized paper-code comparison | Compare as specialized baseline versus RTDL route, with contracts and timing basis stated inline. |

## Partner Choice

| Partner | Use when | Do not claim |
| --- | --- | --- |
| Numba CPU | Small or branchy app logic, CPU fused baselines, no-C++ reference paths. | That it is automatically slower than GPU code. |
| Numba CUDA | Python-source GPU kernels, fused reductions, segmented app continuations. | That it uses RT cores. |
| CuPy | Dense device-array transforms, scans, masks, reductions, CUDA graph-friendly array work. | That it is always faster than Numba. |
| NumPy / CPU exact libraries | Oracles, setup lowering, exact topology, small-scale checks. | That CPU oracle timing is backend-equivalent to RT traversal timing. |
| C++ / CUDA / specialized OptiX | External paper baselines or expert fused hot paths. | That users must write this to use RTDL, or that it is RTDL's normal extension surface. |

For partner-dependent public claims, require a fixed primitive output contract,
the measured best partner, a same-contract Numba reference when relevant, the
same data and timing protocol, and explicit wording that partner choice is not
automatic.

## When To Add A Primitive

Add a new RTDL primitive when all of these are true:

- the operation is app-agnostic enough to be named without the benchmark app;
- keeping it in partner code causes repeated host/device movement,
  row-materialization, synchronization, or duplicated lowering;
- the primitive can define a compact typed output contract;
- there is a CPU/partner oracle for parity;
- OptiX, Embree, or both can implement it without app-specific native-engine
  callbacks;
- the claim boundary says exactly what is and is not accelerated.

Do not add a primitive just to hide app policy inside native code. Barnes-Hut is
the current cautionary example: a naive all-node OptiX any-hit path cannot
preserve parent-acceptance subtree-skip semantics, so RT-native Barnes-Hut
requires a reviewed generic hierarchical traversal lowering first.

## Timing Rules

Always split timing into the phases that affect the decision:

- data loading or generation;
- host-to-device or device-column construction;
- scene/index prepare;
- hot query/replay;
- partner continuation;
- output materialization;
- validation/oracle time.

Do not compare hot RTDL query timing against cold author-code totals unless the
table labels that basis. Do not hide partner setup or data movement when the app
must pay it.

## What RTDL Promises

RTDL promises a disciplined way to express RT-shaped kernels, prepared execution,
app-agnostic primitives, and explicit partner continuation from Python. It aims
to remove unnecessary data movement and materialization inside its own routes.

RTDL does not promise miracles: specialized C++/CUDA/OptiX code can still beat a
generic language/runtime route, especially when it fuses app-specific logic
inside a custom kernel. The useful question is whether RTDL lets the app author
reach a correct, high-performance, honestly measured route without writing that
specialized native code for the common case.
