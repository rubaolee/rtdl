# RayJoin Performance Gap: Problem, Evidence, Challenges, And Next Plan

Date: 2026-07-04

Status: planning_packet_pending_review

## Executive Summary

RTDL now has a correct RayJoin paper-reproduction app for the available
Section 5.2, 5.3, and bounded Section 5.7 workloads. Correctness is no longer
the central problem for the public Section 5.7 sample.

The central problem is performance:

> RTDL's current Section 5.7 route is still much slower than the author's
> C++/CUDA/OptiX implementation because too much of the hot pipeline remains in
> Python application-layer structure assembly, row materialization, and output
> formatting.

The recent optimization work was useful, but mostly as elimination evidence:

- Layer 1/2 row-buffer and Numba handoff are real capabilities.
- Current Numba app helpers do not speed up RayJoin.
- CPU/Numba compiled path-split materialization is correct but slower.
- Prepared-hot PIP traversal is not the bottleneck.
- Final file write is not the bottleneck.

Therefore the next rational step is not another Numba wrapper. The next
authorized step should be:

> Goal4953: a fine-grained measurement of the fastest known plain writer, before
> any native/device writer implementation is allowed.

## What We Are Trying To Solve

The long-term target is not just to run RayJoin correctly. It is to understand
how close RTDL can get to the author's performance while preserving RTDL's
language identity:

- users write Python/RTDL data-flow and app logic;
- RTDL provides generic RT primitives and partner handoff;
- high-performance paths must be generic infrastructure, not a hidden
  RayJoin-specific kernel in RTDL core.

The author implementation is fast because it is a compiled C++/CUDA/OptiX
pipeline. It keeps traversal, filtering, continuation, and output construction
inside compiled code with very little Python-like boundary overhead.

The RTDL implementation is slower because it currently does:

```text
RTDL primitive rows
-> Python app-layer reprojection/sort
-> Python point/chain/face state
-> Python output-chain writer
-> text output
```

That architecture is correct and expressive, but it is not yet author-class
performance.

## Current Performance Facts

Most recent same-POD public-sample numbers from Goal4951:

| Component / Route | Time |
| --- | ---: |
| fastest known plain RTDL Section 5.7 hot run | about `6.26s` |
| plain RTDL output-chain writer | `2.583328s` |
| compiled path-split writer rerun | `4.155936s` |
| compiled path-split relative to plain writer | `0.622x` |
| final text file write in compiled adapter | about `0.043s` |
| prepared-hot vertex PIP total | about `0.020s` |
| LSI rows | about `1.18s` |
| reprojection | about `0.73s` |
| sort map0 + map1 | about `0.80s` |

The author comparator is in the sub-second class on the same public-sample
problem family in earlier evidence. Any exact ratio claim must be tied to a
same-machine, same-input rerun, but the engineering conclusion is already clear:

> RTDL is not within a small constant factor of the author implementation yet.

## What We Already Tried

### Goal4947: LSI Pair Columns To Numba

Goal4947 connected LSI pair columns through the generic row-buffer boundary into
Numba continuation code.

Result:

- capability success;
- no RayJoin performance claim.

### Goal4948: Non-RayJoin Genericity Gate

Goal4948 proved the row-buffer / Numba handoff shape on a non-RayJoin hit-stream
fixture.

Result:

- reduced risk that the connector is RayJoin-only;
- still no RayJoin speed claim.

### Goal4949: RayJoin Hot-Path Remeasure

Goal4949 measured the current RayJoin public-sample route.

After the clean-head erratum, the important facts were:

- baseline and Numba route both remained byte-equal;
- current Numba app helper was slower;
- prepared-hot PIP traversal was tiny;
- the bottleneck was not RT traversal.

Result:

- current app-layer Numba helper must not be promoted.

### Goal4950: Layer 1/2 Closure

Goal4950 closed Layer 1/2 as:

- capability success;
- RayJoin performance no-go.

It authorized moving attention to Layer 3 writer/output assembly.

### Goal4951: Compiled Generic Path-Split Materializer

Goal4951 tested the most conservative Layer 3 route:

```text
app adapter
-> CPU/Numba compiled generic path-split materializer
-> Python app text formatter
```

Gate A/B:

- generic source check passed;
- non-RayJoin synthetic correctness passed;
- Antigravity authorized RayJoin Gate C.

Gate C:

- RayJoin public sample byte-equal to the answer.

Gate D:

- plain writer: `2.583328s`;
- compiled rerun writer: `4.155936s`;
- relative: `0.622x`;
- required minimum: `>=1.10x`.

Result:

- correct but slower;
- route killed as default;
- Antigravity approved closure.

### Goal4952: Post-4951 Decision

Goal4952 stopped the failed CPU/Numba materializer line and authorized only a
measurement goal next:

```text
Goal4953 Plain Writer Fine-Grained Phase Audit
```

Result:

- no new implementation authorized;
- no native/device writer authorized yet;
- no more small variants of the same CPU/Numba materializer route.

## Why The Recent Efforts Did Not Improve Performance

They mostly attacked boundaries and handoff mechanisms, but RayJoin's remaining
cost is deeper:

1. **Layer 1/2 solved connection, not the writer.**
   It proved that RTDL rows can feed Numba through a generic boundary. But the
   writer and structural output assembly remained Python-heavy.

2. **Current app-layer Numba touched the wrong cost shape.**
   Numba helps numeric loops. The dominant writer work includes chain control
   flow, point/polygon ID caches, descriptor state, and string-formatting
   pressure.

3. **CPU/Numba path-split was too late and too materialization-heavy.**
   It preserved byte equality but added generic row-buffer/materialization cost
   large enough to lose to the hand-written app writer.

4. **Final file I/O is tiny.**
   The data says final file write is around `0.04s`. The bottleneck is not
   writing bytes to disk.

5. **Prepared-hot PIP traversal is tiny.**
   PIP traversal is around `0.02s`. The bottleneck is not PIP traversal in this
   public-sample hot state.

## Remaining Challenges

### Challenge 1: The Writer Is Still A Black Box

We know the plain writer costs about `2.58s`, but we do not yet know the exact
distribution inside that number.

Possible sub-costs:

- chain traversal / control flow;
- intersection grouping lookup;
- path interval construction;
- keep/drop decisions;
- point-id cache lookup/insertion;
- polygon-id cache lookup/insertion;
- coordinate formatting;
- header/line string construction;
- list append / buffer construction;
- final write.

Goal4953 must split these rather than guess.

### Challenge 2: Generic Infrastructure Versus RayJoin-Specific Output

RTDL core must not learn the RayJoin paper text format.

Potentially generic:

- grouped output row buffers;
- chain/path segmentation;
- descriptor columns;
- compact binary/columnar output;
- generic native grouped writer infrastructure.

RayJoin app-owned:

- author-compatible text output;
- paper-specific chain numbering;
- paper-specific face/polygon descriptor interpretation;
- comparison labels and reproduction policy.

The difficult design question is where a native/device writer can sit without
becoming a disguised RayJoin writer.

### Challenge 3: Author-Class Performance May Require Fusion Beyond Writer

Even if writer improves, other costs remain:

- LSI rows: about `1.18s`;
- reprojection: about `0.73s`;
- sort: about `0.80s`;
- prepare/session overheads.

To approach author-class sub-second performance, RTDL may eventually need
deeper data-flow fusion:

```text
primitive traversal
-> device-resident continuation
-> grouped output structure
```

That is a larger compiler/runtime direction. It must be treated as a separate
high-risk track, not smuggled into the current RayJoin app.

## Parsed Work Plan

### Goal4953: Plain Writer Fine-Grained Phase Audit

Type: measurement only.

Purpose:

Split the current fastest writer's `~2.58s` into actionable subphases.

Required measurements:

- chain traversal / control flow;
- intersection grouping lookup;
- path interval construction;
- keep/drop decisions;
- point-id cache lookup/insertion;
- polygon-id cache lookup/insertion;
- coordinate formatting;
- header/line string construction;
- list append / buffer construction;
- final file write.

Exit labels:

- `writer_audit_supports_native_generic_writer_goal`
- `writer_audit_shows_app_format_bound_stop`
- `writer_audit_inconclusive_redo`

No implementation is authorized in Goal4953.

### Goal4954: Native/Device Writer Feasibility Plan

Only opens if Goal4953 finds a large recoverable generic structural cost.

Purpose:

Design a native/device writer path that preserves the boundary:

- generic grouped/output infrastructure in RTDL;
- final RayJoin paper formatting in app code.

Required before implementation:

- exact boundary diagram;
- non-RayJoin genericity proof plan;
- byte-equality plan;
- performance gate.

### Goal4955: Non-RayJoin Native Writer Synthetic Gate

Only opens if Goal4954 is approved.

Purpose:

Prove the native/device writer infrastructure on a non-RayJoin fixture first.

Requirements:

- no RayJoin / overlay / Section 5.7 / map0 / map1 semantics;
- exact match to Python reference;
- positive speed signal on synthetic data;
- failure to pass means no RayJoin wiring.

### Goal4956: RayJoin Public Sample Native Writer Gate

Only opens if Goal4955 passes.

Purpose:

Wire the generic native/device writer infrastructure into the RayJoin Section
5.7 public sample as an app adapter.

Required gates:

- byte-for-byte equality;
- same-POD, same-cache comparison against current plain writer;
- minimum writer speedup >= `1.10x`;
- strong writer speedup >= `1.25x`.

If correct but not faster, kill the route.

### Goal4957: Performance Line Decision

Purpose:

Decide whether the RayJoin performance line continues.

Possible exits:

- `native_writer_win_continue_productization`
- `native_writer_correct_but_not_faster_stop`
- `writer_format_bound_stop_rayjoin_perf_line`
- `defer_to_long_term_dataflow_fusion_track`

### Long-Term Track: Data-Flow Fusion Compiler

This is not authorized by Goal4952.

Purpose:

Move selected RTDL data-flow continuations closer to traversal/device execution
without exposing raw OptiX callbacks as the user API.

This is the path that could eventually close more of the author-performance gap,
but it is higher risk and must be run as a separate R&D track.

## Current Recommendation

Proceed only to Goal4953.

Do not implement native writer yet.
Do not implement device writer yet.
Do not make another CPU/Numba materializer wrapper.
Do not make a performance claim.

The immediate job is to measure the fastest plain writer deeply enough to know
whether a generic native/device writer is a real product investment or a
RayJoin-specific rabbit hole.

## Owner-Facing Bottom Line

We have not reached author performance.

We did reach a more mature understanding of why:

- RT traversal is not the current public-sample hot bottleneck;
- final file I/O is not the bottleneck;
- CPU/Numba materialization does not solve the writer;
- the remaining opportunity, if any, is in structural writer/output assembly or
  deeper data-flow fusion.

The next correct move is a measurement gate, not another implementation gamble.
