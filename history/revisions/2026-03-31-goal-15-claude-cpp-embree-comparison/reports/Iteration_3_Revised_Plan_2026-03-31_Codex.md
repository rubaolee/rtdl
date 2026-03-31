# Iteration 3 Revised Plan

Date: `2026-03-31`
Author: `Codex`

## Revised Goal 15 Pre-Action Plan

### Scope

Goal 15 compares:

- RTDL + Embree
- direct C/C++ + Embree

for the current Section 5.6-style workloads:

- `lsi`
- `pip`

The purpose is:

- correctness comparison
- performance comparison
- honest attribution of where RTDL host/runtime overhead exists

### Minimal Native Programs

Implement exactly two standalone native executables first:

1. `apps/goal15_lsi_native.cpp`
2. `apps/goal15_pip_native.cpp`

Both programs:

- generate their own synthetic inputs internally from fixed seeds
- use Embree directly
- emit machine-readable result rows
- emit timing summaries

No file I/O is required in the first slice beyond stdout or optional output files written by the harness.

### Correctness Artifact Format

The correctness artifact format is:

- no header line
- one integer ID pair per line
- sorted lexicographically
- Unix newlines

For `lsi`:

```text
left_id,right_id
```

is **not** used as a header. Instead each line is only:

```text
0,17
0,42
1,3
```

For `pip`, each line is:

```text
point_id,polygon_id
```

again with no header, only data rows.

Optional coordinate/debug outputs may be written separately, but they are not part of the correctness gate.

### LSI Pair-Membership Predicate

The `lsi` correctness gate is based on pair membership only.

Two segments count as intersecting if the current RTDL `reference._segment_intersection(...)` logic would return a non-`None` point:

- non-parallel under epsilon
- intersection parameters satisfy `0 <= t <= 1` and `0 <= u <= 1`

For Goal 15, the native `lsi` implementation should use:

- Embree for candidate filtering
- the same pairwise segment/segment refinement predicate semantics as RTDL for acceptance

This keeps the comparison aligned to RTDL's current implemented semantics, not an idealized exact-geometry semantics.

### PIP Comparison Strategy

The first `pip` comparison should **not** change the semantic object under test by replacing polygons with triangle-fan membership logic.

Instead:

- use Embree only as a broad-phase candidate mechanism over polygon bounds or polygon-associated geometry
- use the same final point-in-polygon refinement semantics as RTDL for membership acceptance
- preserve RTDL's current `boundary_mode=\"inclusive\"` behavior

This keeps the first native comparison semantically aligned with RTDL.

### Oracle Strategy

Use a three-tier oracle strategy:

1. tiny exact fixtures
   - very small hand-checkable datasets
   - may use Python exact arithmetic where useful

2. medium RTDL `run_cpu(...)` parity fixtures
   - same inputs through native Embree and RTDL CPU reference

3. larger RTDL `run_embree(...)` parity fixtures
   - compare native Embree result pairs against RTDL+Embree result pairs
   - timing-focused datasets use these larger fixtures

Pair membership is exact set equality.

Float coordinates, if logged, are debug-only in the first Goal 15 slice.

### Timing Views

Use two timing views:

1. **Native kernel/build timing**
   - includes Embree build
   - includes query traversal
   - includes refinement
   - excludes data generation
   - excludes output formatting/writing

2. **RTDL end-to-end host-path timing**
   - includes RTDL input normalization/materialization
   - includes native backend call
   - excludes synthetic data generation if the harness pre-generates inputs once for both sides

Report these separately. Do not collapse them into a single number.

### First Implementation Slice

Implement only this first:

- `apps/goal15_lsi_native.cpp`
- tiny synthetic fixed-seed input generation inside the program
- sorted pair output with no header
- comparison harness against RTDL `run_cpu(...)` and RTDL `run_embree(...)`

Do not implement `pip` native until the `lsi` native slice passes:

- native vs RTDL CPU pair equality
- native vs RTDL Embree pair equality

### Decision Boundary

If Claude agrees this revised plan fixes the earlier blockers, implementation can begin.
