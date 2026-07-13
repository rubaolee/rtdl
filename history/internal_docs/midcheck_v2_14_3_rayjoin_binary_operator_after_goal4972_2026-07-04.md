# Midcheck — v2.14.3 RayJoin Binary Operator After Goal4972

Date: 2026-07-04

## Executive Summary

We are no longer working on the paper text-writer path as the performance target. The current
performance line is the writer-free RayJoin overlay-as-binary-operator route:

```text
planar-map LSI pair stream
-> device-columnar numeric xsect reprojection
-> device/columnar sort
-> point-location/PIP
-> projected binary descriptor carrier
-> small downstream consumer
```

This is the correct product framing: RTDL is a generic spatial pipeline system, and RayJoin is one
application on top of it. The output-writer remains a correctness sink for paper reproduction, not
the performance target.

Current status:

- The binary route is correct on the top4 County x Zipcode same-source representative.
- Layer 1/2-style device-columnar work moved real cost versus the older public-row route.
- Goal4972 tested and closed one hypothesis: removing the exact LSI count pass does **not** solve
  the remaining bottleneck.
- The next required step is Goal4973: decompose the missing exact LSI producer cost before doing
  more optimization.

## What Has Been Completed

### 1. Binary Route Framing

The project pivoted from:

```text
produce author paper text output as fast as C++/CUDA/OptiX
```

to:

```text
make overlay a writer-free binary intermediate operator in an RTDL spatial pipeline
```

This removes the app-specific text writer from the performance target. The text route still exists
for correctness and paper reproduction, but it is not the benchmark for RTDL's spatial pipeline
value.

### 2. Device-Columnar RayJoin Numeric Route

The current route uses:

- public planar-map LSI and PIP primitives
- Numba CUDA for xsect reprojection and xsect sort
- Numba CPU njit for grouped descriptor scan
- projected descriptor output instead of full author text output

It does not import `rtdsl.rayjoin_overlay`, does not use the bundled helper, and keeps RayJoin
semantics in the app layer.

### 3. Goal4971 — Exact LSI Device Columns On Larger Representative

Goal4971 showed that exact pair-id device columns are correct and useful on the larger top4
representative:

| Route | Writer-Free Hot Sec | LSI Stage |
|---|---:|---:|
| public rows | `7.851479448378086` | `4.313501946628094` |
| exact pair-id device columns | `5.903873108327389` | `2.7495402842760086` |
| prepared replay diagnostic | `2.6364919021725655` | `0.008989743888378143` |

Interpretation:

- exact device columns improve the fresh route;
- prepared replay is diagnostic only because it excludes preparation/workspace cost;
- copying pair-id columns back to NumPy is not the root bottleneck.

### 4. Goal4972 — Bounded Single-Pass Exact LSI Producer

Goal4972 added a bounded exact LSI device-column route:

```text
caller supplies max_rows
native emits exact {left_id, right_id} device columns in a bounded pass
overflow fails closed
```

The route is generic: it outputs only pair ids and does not know RayJoin output chains, author text
format, faces, or overlay semantics.

Validation:

```text
local structural tests: 11 OK, 1 skipped
small crossing smoke: row_count=1, overflow=False
overflow smoke: row_count=0, candidate_event_count=1, overflow=True
```

Top4 representative correctness:

| Gate | Value |
|---|---:|
| LSI row count | `428322` |
| xsect side0 / side1 | `428322 / 428322` |
| vertex PIP positives | `812721 / 4527305` |
| device sort validation | `true / true` |

Top4 representative performance from Goal4972:

| Route | Writer-Free Hot Sec | LSI Stage Sec |
|---|---:|---:|
| public rows | `9.387372702360153` | `4.5479182079434395` |
| exact pair-id device columns | `5.845848858356476` | `2.687378019094467` |
| bounded exact pair-id device columns | `5.277617208659649` | `2.688651569187641` |
| prepared replay diagnostic | `2.56909366697073` | `0.009015299379825592` |

Goal4972 conclusion:

```text
bounded exact LSI: 2.688651569187641s
exact-device LSI: 2.687378019094467s
delta: +0.001273550093174s
```

Therefore, the count pass is not the bottleneck. It was only about `0.002s`, while the Python-measured
exact LSI producer phase is about `2.69s`.

## Current Performance Picture

The current best fresh route in this matrix is:

```text
bounded exact pair-id device columns:
writer_free_hot_sec = 5.277617208659649
```

This is better than public rows but still not close to the author-style fused overlay compute. The
largest unresolved cost is not the downstream writer; it is now inside exact LSI producer cost and
associated setup/warmup boundaries.

Important distinction:

- `prepared replay ~= 2.57s` is useful diagnostic evidence, but it is not a fresh overlay result.
- `bounded exact ~= 5.28s` is a fresh writer-free binary route result.
- The project must not headline the prepared replay number as the real fresh overlay cost.

## The Main Open Problem

Goal4972 exposed an accounting gap:

```text
Python phase for bounded exact LSI ~= 2.6887s
native output traversal/write      ~= 0.0023s
unaccounted                         ~= 2.6864s
```

The unaccounted time could be:

- runtime pipeline compilation or NVCC fallback
- OptiX module/pipeline/SBT setup
- grouped-range or scaled-segment workspace construction hidden outside current timers
- stream synchronization placement
- per-process initialization caused by the measurement harness

We do not yet know which one dominates. More optimization without measuring this would be
guesswork.

## Environment Notes

The POD used for Goal4972 required:

```text
RTDL_OPTIX_PTX_COMPILER=nvcc
explicit PATH and LD_LIBRARY_PATH
```

Reason:

- NVRTC failed on host glibc math headers in the runtime exact-count kernel path.
- nvcc fallback worked once PATH included `/usr/bin` and CUDA/libnvvm paths were explicit.

This is a measurement-environment fix, not a RayJoin semantics change.

## Next Plan

### Goal4973 — Exact LSI Producer Cost Decomposition

Purpose:

Locate the `~2.686s` missing exact LSI producer cost before implementing further optimizations.

Work:

1. Add native phase timing around:
   - scaled segment cache ensure
   - grouped range ensure
   - exact-count pipeline ensure/compile
   - split-pair-id kernel ensure
   - OptiX launch
   - split kernel
   - DtoH copy
2. Add same-process repeated-run diagnostic:
   - first bounded exact run
   - second bounded exact run on the same prepared query
   - third bounded exact run after explicit workspace preparation
3. Re-run top4 representative and preserve correctness gates.

Decision branches:

- If pipeline/module compilation dominates: build reusable exact LSI pipeline/session cache.
- If workspace setup dominates: make workspace preparation explicit and reusable.
- If traversal dominates after warm setup: target exact LSI predicate/traversal implementation.
- If host copy dominates: resume resident downstream work.

### After Goal4973

The next implementation goal depends on the phase table:

| Dominant Cost | Next Goal |
|---|---|
| compile/module setup | reusable exact LSI pipeline cache |
| workspace setup | explicit resident exact LSI workspace |
| traversal/predicate | exact planar-map LSI predicate/traversal optimization |
| host copy | resident downstream continuation |

## Boundaries

Still not authorized:

- no RayJoin-specific core kernel
- no author-performance headline
- no Layer 4 callback/fusion claim
- no public release wording from these internal measurements
- no overclaim that bounded single-pass solved the exact LSI bottleneck

## Files

Goal4972 result:

`history/internal_docs/goal4972_bounded_single_pass_exact_lsi_producer_result_2026-07-04.md`

Goal4972 review request:

`history/internal_docs/call_for_review_goal4972_bounded_single_pass_exact_lsi_producer_result_2026-07-04.md`

Goal4972 artifacts:

`history/internal_docs/goal4972_bounded_single_pass_exact_lsi_producer_artifacts_2026-07-04/`

Goal4973 proposed next goal:

`history/internal_docs/goal4973_exact_lsi_producer_cost_decomposition_goal_2026-07-04.md`

Goal4973 review request:

`history/internal_docs/call_for_review_goal4973_exact_lsi_producer_cost_decomposition_goal_2026-07-04.md`
