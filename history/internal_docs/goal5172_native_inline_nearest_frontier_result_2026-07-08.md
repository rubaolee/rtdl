# Goal5172 Native Inline-Nearest Frontier Result

Date: 2026-07-08

## Verdict

```text
completed_native_inline_nearest_frontier_route__implemented_review_pending
```

Goal5172 adds an app-neutral native inline-nearest mode to the generic 3-D
cell-MBR frontier collector. Inline cell rows can now compute nearest-witness
payload state during native traversal and emit only offload rows to the
downstream continuation. This closes a real route boundary without adding an
X-HD-specific primitive.

This is implemented and POD-validated. It is not externally reviewed yet.

## What Changed

### Native OptiX

Files:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`

New public native symbol:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
```

The v3 collector extends the generic 3-D cell-MBR frontier collector with:

- `inline_nearest`;
- target point columns;
- target point ids;
- cell point row indices;
- nearest distance outputs;
- nearest item-id outputs.

When `inline_nearest=true`, native traversal handles rows with
`frontier_kind=inline` by scanning the cell's target point range in the any-hit
path, updating a per-query nearest payload using double-precision squared
distance and lower-item-id tie break. Inline rows are not emitted to the row
table. Offload rows are still emitted for downstream continuation.

The old v1/v2 behavior is preserved:

- v1 is the original sorted mode;
- v2 adds `sort_rows`;
- v3 adds inline nearest.

### Python RTDL Surface

Files:

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/partner_continuations.py`

`collect_cell_mbr_nearest_frontier_3d_optix(...)` now exposes the v3 path behind
`inline_nearest=True`, requiring target columns and point row indices. The
wrapper fails closed if the v3 symbol or required inputs are missing.

`cell_mbr_nearest_frontier_native_3d_optix_columns(...)` now accepts:

```text
target_point_columns
inline_nearest
```

When inline mode is used, the returned `nearest_state` is initialized from the
native nearest-output columns rather than from the original seed alone.

### X-HD Paper App Route

Files:

- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py`

New CLI flag:

```text
--frontier-inline-nearest
```

The app route passes the generic target point columns into the RTDL native
frontier helper and consumes the returned native nearest state before running
the remaining offload continuation.

## Genericity Boundary

The new system capability is:

```text
generic 3-D cell-MBR frontier traversal with optional inline nearest witness
payload reduction
```

It does not encode:

- X-HD;
- Hausdorff distance;
- Stanford/Dragon/HappyBuddha;
- author `hd_exec`;
- paper-specific tolerance;
- paper-specific output/comparator semantics.

The X-HD app only opts into the generic mode because its streaming route can use
inline cell results directly and only needs offload rows downstream.

## Validation

### Local Tests

```text
py -m unittest tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5171_unsorted_native_frontier_rows_test \
  tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test

Ran 20 tests OK
```

The focused Goal5172 test verifies:

- partner wrapper passes target point columns and point row indices to native;
- native nearest-state output is used by the downstream route;
- runtime fails closed unless the v3 symbol is available for inline mode;
- route and matrix CLIs expose `--frontier-inline-nearest`;
- native API/header declare v3 and nearest output arrays.

### POD Build And Tests

POD:

```text
host = 213.173.108.24
port = 13502
remote repo = /root/rtdl_goal5093
GPU = NVIDIA RTX 4000 Ada Generation
```

Build:

```text
make build-optix
```

Focused POD tests:

```text
python3 -m unittest \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5171_unsorted_native_frontier_rows_test \
  tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 23 tests OK
```

## POD Evidence

All evidence is Level B same-source Stanford graphics evidence, not exact paper
dataset reproduction.

### Full Public Stanford Res4 Inline-Nearest Matrix

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_inline_nearest_matrix_pod.json
```

Key fields:

```text
case = res4full
point_count_a = 5205
point_count_b = 7108
matched = true
author HDResult = 0.1241602823138237
RTDL comparison distance = 0.12416027787377293
author_abs_diff = 4.440050771492565e-09
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
frontier_inline_nearest = true
route_sec_median = 0.029158174991607666
total_sec_median = 0.06985066831111908
ratio fields = null
```

Direction details:

```text
A -> B:
  frontier rows = 98
  continuation candidate distance evaluations = 7354
  total candidate distance evaluations = 200671
  frontier median = 0.005167119204998016 s
  continuation median = 0.002048991620540619 s
  seed median = 0.0030991211533546448 s

B -> A:
  frontier rows = 0
  continuation candidate distance evaluations = 0
  total candidate distance evaluations = 188251
  frontier median = 0.004643425345420837 s
  continuation median = 0.0019671767950057983 s
  seed median = 0.003113970160484314 s
```

### Same-Rebuild No-Inline Control

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_native_no_inline_control_matrix_pod.json
```

Key fields:

```text
matched = true
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2
frontier_inline_nearest = false
route_sec_median = 0.03279334306716919
total_sec_median = 0.07399309426546097
```

Direction details:

```text
A -> B:
  frontier rows = 17964
  continuation candidate distance evaluations = 612923
  total candidate distance evaluations = 806240
  frontier median = 0.00378035008907318 s
  continuation median = 0.00422513484954834 s
  seed median = 0.00343339145183563 s

B -> A:
  frontier rows = 21910
  continuation candidate distance evaluations = 539093
  total candidate distance evaluations = 727344
  frontier median = 0.00418967753648758 s
  continuation median = 0.00442077964544296 s
  seed median = 0.00322479754686356 s
```

### Same-Rebuild Delta

```text
route median:
  no-inline control = 0.03279334306716919 s
  inline nearest    = 0.029158174991607666 s
  delta             = -0.0036351680755615234 s
  relative route win = about 11.1%

total median:
  no-inline control = 0.07399309426546097 s
  inline nearest    = 0.06985066831111908 s
  delta             = -0.004142425954341888 s
  relative total win = about 5.6%

continuation candidate distance evaluations:
  no-inline control = 612923 + 539093 = 1152016
  inline nearest    = 7354 + 0 = 7354
```

Interpretation: native inline-nearest removes nearly all downstream
continuation candidate evaluations, but transfers some work into the native
frontier phase. The route-time win is real but modest.

### Sample256 Exact-And-Author Smoke

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5172_inline_nearest_exact_smoke_pod.json
```

Key fields:

```text
case = sample256
matched = true
rtdl_matches_exact_reference = true
author_abs_diff = 2.6291111787646315e-09
rtdl_exact_abs_diff = 0.0
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
route_sec_median = 0.006261758506298065 s
total_sec_median = 0.11209642887115479 s
exact_reference_sec_median = 0.10451782494783401 s
validation_mode = exact-and-author
```

Both directions emitted zero offload frontier rows under inline-nearest mode,
so the smoke verifies the all-inline correctness case.

## What This Proves

- The v3 native inline-nearest mode builds and runs on CUDA/OptiX POD.
- It preserves X-HD Level B same-source correctness on full public Stanford res4.
- It preserves exact-reference correctness on sample256.
- It is app-neutral at the RTDL/native API surface.
- It reduces downstream continuation work dramatically.
- It improves same-rebuild full-res4 route median from about 32.79 ms to about
  29.16 ms.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not authorize an author-vs-RTDL speedup or parity ratio.
- It does not align author `Running.AvgTime` with RTDL route time.
- It does not implement the full author X-HD fused RT-core algorithm.
- It does not make Hausdorff or X-HD a special RTDL core primitive.

## Updated Artifacts

Manifest updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

New artifact entries:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_native_no_inline_control_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_inline_nearest_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5172_inline_nearest_exact_smoke_pod.json
```

Review register updated:

```text
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

Status:

```text
Goal5172 implemented; review pending
```
