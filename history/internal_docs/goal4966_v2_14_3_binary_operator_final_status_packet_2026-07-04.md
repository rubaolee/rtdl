# Goal4966 v2.14.3 Binary Operator Final Status Packet

Date: 2026-07-04

## Exit Label

`completed_v2_14_3_binary_operator_arc__fresh_overlay_3x_improved__exact_lsi_remains_bottleneck`

## Purpose

Close the Goal4959-Goal4966 arc.

This packet states what v2.14.3 achieved for the RayJoin paper-reproduction
binary-operator route, what it did not achieve, and what the next credible
engineering direction is.

The core correction of this arc was:

> Stop benchmarking RTDL as a text-dumping standalone RayJoin program, and
> measure the writer-free binary overlay operator that a downstream dataflow
> pipeline would actually consume.

That correction is valid. It removed the app-specific text writer from the
performance question. It did not by itself close the fresh overlay compute gap.

## Summary In One Table

Same public input throughout:

```text
left:  br_county_clean_25_odyssey_final.txt
right: br_soil_ascii_odyssey_final.txt
AuthorPatch overlay compute comparator: 0.0421s
```

| Route / Claim Boundary | Median | Ratio vs AuthorPatch `0.0421s` | Meaning |
|---|---:|---:|---|
| Earlier numeric binary route before device-columnar work | ~`2.92s` | ~`69x` | Writer-free, but still heavy Python/CPU stages |
| Fresh device-columnar writer-free route | `0.889023s` | ~`21x` | Real v2.14.3 improvement, about `3.3x` faster than earlier route |
| Prepared-hot workspace replay | `0.087069s` | not comparable as fresh overlay | Reruns pair-id rows on an already prepared workspace; excludes workspace/cache build |
| Exact pair-id device-column route | `0.987424s` | ~`23x` | Correct, but slower than host exact pair-id rows |

## What Was Completed

### 1. The bad `2.04x` headline was closed

Goal4959 corrected the measurement boundary:

- `0.086-0.087s` excludes the first exact LSI computation.
- It must be labeled as cached/prepared replay, not fresh overlay.
- It cannot be compared directly to AuthorPatch fresh overlay compute.

Allowed claim:

```text
Fresh writer-free binary overlay is about 0.89s on the public sample.
Cached replay after LSI is already computed is about 0.087s.
```

Forbidden claim:

```text
RTDL fresh overlay is only about 2x slower than AuthorPatch.
```

### 2. Fresh vs prepared-hot same-input measurement was run

Goal4960 measured the same input in both modes.

Artifacts:

```text
history/internal_docs/goal4955_artifacts/goal4960_fresh_run1.json
history/internal_docs/goal4955_artifacts/goal4960_fresh_run2.json
history/internal_docs/goal4955_artifacts/goal4960_fresh_run3.json
history/internal_docs/goal4955_artifacts/goal4960_cached_replay_run1.json
history/internal_docs/goal4955_artifacts/goal4960_cached_replay_run2.json
history/internal_docs/goal4955_artifacts/goal4960_cached_replay_run3.json
history/internal_docs/goal4955_artifacts/goal4960_fresh_vs_cached_same_input_summary.json
```

Key numbers:

```text
fresh median:         0.8890228355303407s
prepared-hot median:  0.08706910163164139s
```

Post-Goal4967 refinement: this prepared-hot route is not merely reading a
cached pair-id result. It calls the native pair-id row path again, but after the
planar-map LSI workspace and first-use caches have already been prepared. It is
therefore still not a fresh one-shot overlay cost.

Stable semantic fingerprint:

```text
pair_count       = 28815
total_groups     = 64459
total_point_rows = 673371
```

### 3. Larger representative input availability was audited

Goal4961 checked the current POD for historical larger representative inputs.

Only the public sample was present:

```text
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_countyXbr_soil_answer.txt
data/public_sample_manifest.json
```

Historical larger inputs were missing from `/root`, `/workspace`, `/tmp`, and
`/dev/shm`.

Goal4962 therefore remains:

```text
blocked_by_representative_input_availability
```

This is recorded explicitly in:

```text
history/internal_docs/goal4962_larger_representative_input_run_blocked_2026-07-04.md
```

This is not a performance result. It is an input availability boundary.

### 4. Exact LSI pair-id device columns were designed and implemented

Goal4963 defined the missing route:

```text
exact planar-map LSI -> generic {left_id,right_id} device columns
```

Goal4964 implemented and measured it.

Core/API work:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal4964_exact_lsi_pair_id_device_columns_test.py
tests/goal4956_columnar_xsect_pipeline_test.py
```

New native symbol:

```text
rtdl_optix_run_prepared_segment_pair_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode
```

New Python route:

```python
PreparedOptixPlanarMapLsi2DQuery.run_pair_id_device_columns()
PreparedOptixPlanarMapLsi2D.run_pair_id_device_columns(query)
```

App measurement flag:

```bash
--exact-lsi-device-columns
```

### 5. Exact LSI device columns passed correctness but failed performance

Goal4964 POD median results:

| Route | writer_free_hot_sec | Ratio vs `0.0421s` | LSI phase | Device-to-NumPy copy |
|---|---:|---:|---:|---:|
| host exact pair-id rows | `0.893045s` | `21.21x` | `0.806946s` | n/a |
| exact pair-id device columns | `0.987424s` | `23.45x` | `0.895913s` | `0.000526s` |

Stable fingerprint in all runs:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

Decision:

```text
Do not promote --exact-lsi-device-columns as the v2.14.3 performance route.
```

The copy/marshalling hypothesis was falsified for this route:

```text
device-to-NumPy copy: ~0.000526s
exact LSI phase:      ~0.895913s
```

The bottleneck is not pair-id copy. The bottleneck is fresh exact LSI compute.

### 6. The bottleneck decision was recorded

Goal4965 concluded:

```text
The next credible performance target is exact planar-map LSI fresh cost.
```

The next goal should measure and attack:

- whether the count+emit two-pass exact route is removable,
- whether exact predicate/traversal dominates,
- whether exact pair-id production can be single-pass,
- whether the remaining gap is a later pushdown/fusion problem.

## What v2.14.3 Actually Achieved

### Real improvement

The writer-free binary route improved from about:

```text
~2.92s -> ~0.889s
```

That is about:

```text
~3.3x faster
```

This is real and useful. It came from the device-columnar / compiled grouping
work that finally applied the Layer-1/2 direction to the RayJoin binary route.

### Real boundary

Even after that improvement, fresh overlay remains about:

```text
0.889s / 0.0421s = ~21x slower than AuthorPatch overlay compute
```

The main remaining cost is exact LSI:

```text
host exact LSI phase: ~0.806946s
```

That single phase is already about:

```text
~19x AuthorPatch overlay compute
```

So the fresh-overlay performance problem is now much sharper and narrower:

```text
exact planar-map LSI fresh compute
```

## What v2.14.3 Did Not Prove

It did not prove:

- near-AuthorPatch fresh overlay performance,
- that cached replay is the fresh overlay cost,
- that exact device columns speed up the route,
- that candidate LSI device columns are correctness-equivalent,
- that larger representative inputs behave the same way,
- that RTDL has closed the in-traversal fusion gap,
- that text-dump RayJoin is the right benchmark for RTDL's dataflow value.

## Current Status Of Goals 4959-4966

| Goal | Status | Evidence |
|---|---|---|
| 4959 | complete | `goal4959_close_goal4958_erratum_and_claim_boundary_2026-07-04.md` |
| 4960 | complete | `goal4960_fresh_vs_cached_same_input_measurement_2026-07-04.md` and artifacts |
| 4961 | complete | `goal4961_larger_representative_input_availability_audit_2026-07-04.md` |
| 4962 | blocked by input availability | `goal4962_larger_representative_input_run_blocked_2026-07-04.md`; no larger inputs on current POD |
| 4963 | complete | `goal4963_exact_lsi_pair_id_device_columns_design_gate_2026-07-04.md` |
| 4964 | complete | `goal4964_exact_lsi_pair_id_device_columns_result_2026-07-04.md` and artifacts |
| 4965 | complete | `goal4965_exact_lsi_bottleneck_decision_after_device_columns_no_go_2026-07-04.md` |
| 4966 | complete | this status packet |

## Recommended Next Goals

These are not part of the 4959-4966 closure, but they are the next honest
engineering path.

### Goal4967: Exact Planar-Map LSI Fresh Cost Breakdown

Purpose:

- break down the `~0.806946s` exact LSI phase,
- determine whether count+emit double work, predicate/traversal, or refinement
  dominates,
- choose the smallest grounded implementation step.

### Goal4968: Single-Pass Exact Pair-Id Production Feasibility

Only open this if Goal4967 shows that double-pass exact output is a real
removable cost.

### Goal4969: Exact Planar-Map LSI Predicate/Traversal Optimization

Only open this if Goal4967 shows the predicate/traversal path dominates and has
specific removable work.

### Goal4970: Restore Larger Representative Dataset

Restore at least one larger representative input, preferably the South America
bounded sample or the prior same-source County x Zipcode / Block x Water CDBs,
and rerun the fresh writer-free binary route.

### Future Layer-4 Goal

If exact LSI compute remains fundamentally slower because RTDL performs work
outside traversal that AuthorPatch fuses inside traversal, then the correct
next line is the later dataflow-to-traversal pushdown/fusion compiler work.
That is not proven by v2.14.3, and it should be separately gated.

## Public Claim Boundary

Allowed:

```text
The v2.14.3 RayJoin binary-operator work produced a writer-free fresh overlay
route on the public sample that is about 3.3x faster than the earlier numeric
binary route, while preserving the expected semantic fingerprint. Fresh overlay
remains about 21x slower than the AuthorPatch overlay-compute comparator, with
exact planar-map LSI fresh compute now the dominant bottleneck.
```

Forbidden:

```text
RTDL is near AuthorPatch performance.
RTDL fresh overlay is 2x slower than AuthorPatch.
Exact LSI device columns are the speedup route.
Cached replay is fresh overlay performance.
Larger representative performance has been shown.
Candidate device columns are exact.
RayJoin-specific core logic was required or approved.
```

## Final Decision

Close the 4959-4966 arc as:

```text
fresh binary operator improved, measurement boundary corrected, exact LSI
device-column route no-go, exact LSI fresh compute identified as next
bottleneck, larger representative testing blocked by missing inputs.
```
