# Goal5276 - X-HD RTDL Bounded Memory Matrix

## Status

`implemented_review_pending`

## Goal

Convert the Goal5275 native telemetry artifacts into a reviewable RTDL-side
memory matrix.  The matrix is explicitly bounded/status-bearing and does **not**
claim to reproduce author Figure 11.

## What Changed

Added app-owned helper:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
```

The helper reads hd_exec-compatible RTDL JSON artifacts with
`RTDL.memory_accounting` and emits rows with:

- input paths and point counts,
- selected RTDL route label,
- HDResult,
- author-mapped status-bearing fields (`BVH`, `Grid`, `MBRs B`, `WL`,
  `WL Heavy Peak`),
- RTDL-only fields,
- explicit `same_denominator_author_figure11=false`,
- matrix-level claim boundary flags all false.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
```

Matrix summary:

```text
schema: rtdl.paper_reproduction.xhd.rtdl_memory_matrix.v1
row_count: 2
measured_bvh_rows: 2
wl_heavy_peak_unavailable_rows: 2
all_rows_same_denominator_author_figure11: false
figure11_reproduced: false
author_memory_parity_claimed: false
same_denominator_author_figure11_claimed: false
```

Rows:

```text
tiny3d native telemetry probe
  BVH: 896 bytes (measured native OptiX accel output buffer)
  WL Heavy Peak: unavailable

stanford dragon->happy sample256 native telemetry probe
  BVH: 7552 bytes (measured native OptiX accel output buffer)
  WL Heavy Peak: unavailable
```

## Why This Is Useful

Before Goal5275, RTDL-side `BVH` was opaque/unavailable.  After Goal5275 and
Goal5276, reviewers can inspect a real matrix row where:

- `BVH` has measured native OptiX GAS output-buffer bytes,
- `Grid` and `MBRs B` remain contract estimates,
- `WL` remains a row-capacity estimate,
- `WL Heavy Peak` remains unavailable,
- no author Figure 11 ratio is reported.

This puts the remaining Figure 11 gap into a concrete table instead of prose.

## Validation

```text
py -m unittest \
  tests.goal5276_xhd_rtdl_bounded_memory_matrix_test \
  tests.goal5275_xhd_native_memory_telemetry_contract_test \
  tests.goal5275_xhd_native_memory_telemetry_artifact_test \
  tests.goal5274_xhd_hd_exec_memory_accounting_integration_test \
  tests.goal5273_xhd_rtdl_memory_accounting_test

Ran 14 tests in 1.560s
OK
```

Compilation:

```text
py -m py_compile \
  Paper-reproduction-apps\x-hd-paper\scripts\xhd_rtdl_memory_matrix.py \
  tests\goal5276_xhd_rtdl_bounded_memory_matrix_test.py
```

JSON parsing:

```text
xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json parses successfully.
```

## Claim Boundary

Allowed:

- RTDL now has a bounded/status-bearing memory matrix for the current native
  cell-MBR telemetry artifacts.
- The matrix includes measured native OptiX GAS output-buffer bytes in the
  `BVH` field.
- The matrix makes unavailable and estimated fields explicit.

Forbidden:

- Figure 11 reproduced.
- author memory parity.
- exact GPU allocator peak accounting.
- author same-denominator memory ratio.
- WL Heavy Peak measured.
- full X-HD paper reproduction.

## Remaining Gap

Goal5276 makes the RTDL memory evidence reviewable as rows, but it still leaves
the core Figure 11 blockers:

```text
WL Heavy Peak is unavailable.
RTDL Grid/MBRs/WL fields are not author allocator fields.
Input rows are bounded probes, not exact paper Figure 11 datasets.
No same-denominator author-vs-RTDL memory ratio is authorized.
```

The next substantive choices are:

1. implement peak/heavy-worklist telemetry, or
2. request review acceptance that RTDL's route does not have an author-like
   heavy worklist denominator and therefore Figure 11 can only be reported as
   non-comparable RTDL-side memory evidence.
