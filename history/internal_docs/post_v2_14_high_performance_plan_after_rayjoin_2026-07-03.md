# Post-v2.14 High-Performance Plan After RayJoin

Date: 2026-07-03

Status: `plan_for_external_review__not_a_goal__not_implementation_authorization`

## Purpose

Define the next high-performance development plan after the v2.14 RayJoin
paper-reproduction work.

This document is a planning and review artifact only. It does not authorize
implementation. If reviewers approve the plan, a separate numbered goal should
be created and executed.

## Current Facts

The v2.14 RayJoin reproduction line has reached a bounded correctness result:

- Section 5.2 LSI reproduced;
- Section 5.3 PIP / point-location reproduced;
- Section 5.7 polygon overlay reproduced in a bounded form with public RTDL
  primitives and an agreed AuthorPatch / AuthorOfficial comparator;
- Numba partner acceleration produced a real app-layer writer improvement.

The strongest recent performance facts on the Australia representative
Section 5.7 workload are:

| View | AuthorPatch C++/CUDA/OptiX | RTDL+Python | RTDL+Python+Numba v2 | Meaning |
| --- | ---: | ---: | ---: | --- |
| One-shot end-to-end | `148.939 s` logged phase sum | `117.258 s` | `103.786 s` | RTDL+Numba is faster in this cold one-shot view. |
| Query + output, excluding read/build | `0.844 s` | `36.076 s` | `20.920 s` | AuthorPatch is `24.78x` faster than RTDL+Numba. |
| Core query compute, excluding read/build and output write | `0.0421 s` | `19.550 s` | `18.880 s` | AuthorPatch is `448.47x` faster than RTDL+Numba. |

The important conclusion:

```text
Correctness is now the strong result.
Hot-path performance is still not solved.
```

## Root Diagnosis

The root difference is not merely that RTDL lacks a callback API.

The real distinction is:

```text
OptiX lets user computation run inside traversal kernels.
RTDL currently places most user computation after traversal, on materialized rows.
```

This creates:

1. an expression gap;
2. a fusion/performance gap.

The next high-performance line must therefore avoid two false paths:

- pretending that prettier Python wrappers solve the kernel-placement problem;
- exposing raw OptiX callbacks as the primary RTDL programming model.

The desired long-term direction is:

```text
users write data-flow / ITRE;
RTDL decides what can be pushed down or fused into traversal;
unfused work runs through explicit, measured partner continuation.
```

## What V3/V4 Contributed And What They Did Not

V3/V4 are sealed experimental work and are not current user-facing releases.
However, their lessons matter.

Reusable lessons:

- prepared/execution-graph intent was right;
- partner continuation was the right abstraction;
- phase accounting is mandatory;
- operator fusion must remain app-agnostic;
- wrapper-first API without engine changes is not enough.

Non-reusable mistakes:

- overclaiming before proving the performance source;
- turning local route wins into release claims;
- confusing app-specific helper code with language capability;
- trying to sell broad speedups without app-level evidence.

## Plan Overview

The plan has four stages.

```text
Stage 0: External review of this plan.
Stage 1: Measurement gate: decompose the 18.880 s core bucket.
Stage 2: Branch according to measured bottleneck.
Stage 3: Implement only the branch justified by measurement.
```

No implementation should begin before Stage 0 approval.

## Stage 0: External Review

Ask reviewers whether this plan:

- correctly understands the RayJoin performance evidence;
- correctly accepts the Goal4887 block;
- prevents another V3-style implementation-before-source mistake;
- keeps RayJoin as an exam rather than a product model;
- chooses a reviewable measurement gate before implementation.

Exit:

```text
approved_to_create_measurement_goal
```

or:

```text
blocked_plan_needs_rewrite
```

## Stage 1: Measurement Gate

Before implementation, decompose:

```text
RTDL+Numba v2 core query compute = 18.880 s
```

This is already drafted as:

```text
history/internal_docs/goal4888_core_phase_decomposition_gate_2026-07-03.md
```

The decomposition must separate:

- public RTDL LSI traversal / row production;
- LSI row materialization or row download;
- intersection reprojection;
- sorting;
- vertex PIP traversal;
- vertex PIP upload/download/materialization;
- midpoint generation;
- midpoint PIP traversal;
- Numba continuation;
- Python orchestration;
- host/device transfer or materialization where measurable.

The measurement goal must not:

- modify `src/rtdsl/**`;
- modify `src/native/**`;
- implement prepared sessions;
- implement row-buffer ABI;
- implement partner APIs;
- add RayJoin-specific shortcuts.

Exit labels:

- `native_rt_traversal_dominated`
- `host_materialization_dominated`
- `python_orchestration_dominated`
- `mixed_but_fusion_plausible`
- `insufficient_instrumentation`

## Stage 2: Branch By Evidence

### Branch A: Host / Python / Materialization Dominated

If measurement shows that most of the `18.880 s` core bucket is due to
host/Python/materialization overhead, then proceed with generic engine work:

- prepared planar-map sessions;
- stable row-buffer ABI;
- formal Numba partner continuation;
- materialization-aware pipeline;
- device-resident continuation where possible.

This branch may keep a performance target, but the target must be computed
from the measured removable cost.

### Branch B: Native RT Traversal Dominated

If measurement shows that most of the `18.880 s` core bucket is native RT
traversal / primitive work, then prepared sessions and Numba continuation are
still useful engineering but are not enough for the hot-path goal.

The next high-performance work must then shift to:

- generic native primitive/kernel improvement;
- recognized operator pushdown into traversal;
- generic data-flow fusion compiler work;
- algorithmic candidate pruning;
- or a no-speed-promise engineering hygiene goal.

This branch must not sell prepared/session work as a path to `3-8 s` unless the
native primitive cost is also reduced.

### Branch C: Mixed But Fusion Plausible

If both materialization and native traversal matter:

- split the goal into two tracks;
- remove measured host/Python/materialization first;
- separately design generic pushdown for the native-dominated part.

### Branch D: Insufficient Instrumentation

If the existing summaries cannot support a bottleneck classification:

- do not implement high-performance features yet;
- first add bounded instrumentation in external harnesses or safe measurement
  hooks;
- keep implementation blocked.

## Stage 3: Implementation Options After The Gate

Only the evidence-supported branch may become an implementation goal.

### Option 1: Generic Prepared Session

Purpose:

- avoid repeated CDB parse / load-pack / prepared map construction;
- separate cold run from prepared hot run.

Generic output:

```python
left = rtdl.planar_map.from_cdb("left.cdb")
right = rtdl.planar_map.from_cdb("right.cdb")

with rtdl.prepare_planar_map_session(left, right) as session:
    ...
```

Not allowed:

- `prepare_rayjoin_session`;
- hidden Section 5.7 fast paths.

### Option 2: Stable Row-Buffer ABI

Purpose:

- make LSI/PIP outputs stable and reusable;
- allow partners to consume RTDL outputs without ad-hoc Python glue.

Example:

```text
LSIRows:
  left_edge_id
  right_edge_id
  intersection_x_num
  intersection_y_num
  flags

PointLocationRows:
  point_id
  face_id
  closest_edge_id
  classification
  flags
```

Not allowed:

- row schemas named after RayJoin;
- output-chain-specific core schemas.

### Option 3: Formal Numba Partner Continuation

Purpose:

- replace monkeypatch-style app acceleration with a reviewed partner API;
- keep partner choice explicit.

Example:

```python
out = session.continue_with_numba(
    inputs=[lsi_rows, pip_rows],
    kernel=user_kernel,
    output_schema="custom_rows",
)
```

Not allowed:

- automatic hidden partner selection;
- treating Numba as correctness-critical for existing reproduction evidence.

### Option 4: Generic Data-Flow Pushdown / Fusion Compiler

Purpose:

- move recognized data-flow operations into traversal when safe;
- attack the actual fusion gap without exposing raw OptiX callback as the main
  user model.

Possible recognized operators:

- count;
- sum;
- min/max;
- threshold;
- mask/filter;
- compact;
- top-k / nearest candidate;
- grouped reduction.

Not allowed:

- raw any-hit / closest-hit callback as the primary public model;
- RayJoin-specific fused overlay kernel as the first proof.

## Performance Targets

Do not use these as promises. They are provisional and must be revised after
Stage 1 measurement.

Current baseline:

```text
RTDL+Numba v2 one-shot end-to-end: 103.786 s
RTDL+Numba v2 query+output:         20.920 s
RTDL+Numba v2 core query compute:   18.880 s
AuthorPatch query+output:            0.844 s
AuthorPatch core query compute:      0.0421 s
```

Reasonable target if measurement proves materialization/Python dominated:

```text
prepared hot query+output: 3-8 s
```

Reasonable target if measurement proves native traversal dominated:

```text
no 3-8 s target without native primitive/operator pushdown work
```

Stretch target:

```text
<= 1.5 s prepared query+output
```

This requires explicit re-approval after Stage 1. It should not survive if the
core bucket is native traversal dominated.

## Success Criteria For The First Implementation Goal

If Stage 0 and Stage 1 approve implementation, the first implementation goal
must:

1. be generic;
2. have one clear bottleneck target;
3. preserve RayJoin representative byte equality;
4. produce phase accounting;
5. show improvement against the correct baseline;
6. document what did not improve;
7. avoid public release wording.

## Kill Conditions

Stop or rewrite the implementation goal if:

- it needs a RayJoin-specific API;
- it needs private `rayjoin_overlay` helpers;
- it cannot explain which measured bottleneck it attacks;
- it only improves cold end-to-end while leaving the intended hot target
  unchanged;
- it hides native traversal dominance behind wrapper language;
- it makes a performance claim without denominator and phase boundary.

## External Review Questions

1. Does this plan correctly separate correctness completion from hot-path
   performance failure?
2. Does it correctly accept the Goal4887 block?
3. Is Stage 1 measurement the right next step before implementation?
4. Are the branch conditions sharp enough?
5. Is the plan truly generic, or does it still smuggle RayJoin into the engine?
6. Are the performance targets appropriately provisional?
7. Should a formal measurement goal be created from this plan?

## Non-Authorization

This document does not authorize:

- implementation;
- public release wording;
- prepared-session code;
- row-buffer ABI code;
- Numba partner API code;
- native kernel work;
- raw callback API work;
- RayJoin-specific shortcuts;
- changing comparator boundaries;
- claiming hot-path parity with AuthorPatch.
