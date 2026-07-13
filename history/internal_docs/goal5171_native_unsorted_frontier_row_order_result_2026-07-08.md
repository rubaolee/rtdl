# Goal5171 Native Unsorted Frontier Row Order Result

Date: 2026-07-08

## Verdict

```text
completed_native_unsorted_frontier_row_order__small_route_win
```

Goal5171 adds a compatibility-preserving native frontier row-order policy for
the generic 3-D cell-MBR nearest-frontier collector. The legacy behavior remains
sorted+unique by default. Streaming consumers that do their own grouping can now
request native emission order and avoid the host-side `std::sort + unique` step
inside the native collector.

This is a small RTDL route improvement, not a full X-HD paper reproduction claim
and not an author-performance ratio.

## Implementation

### Generic native ABI

The existing symbol remains unchanged and keeps legacy behavior:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d(...)
```

It forwards to the internal collector with `sort_rows=1`.

Goal5171 adds:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2(..., emit_pruned_rows, sort_rows, row_capacity, ...)
```

The implementation changes the internal collector from unconditional sorting to:

```cpp
if (sort_rows) {
    std::sort(...);
    rows.erase(std::unique(...), rows.end());
}
```

This keeps default compatibility and makes unsorted/native emission an explicit
caller decision.

### Python public/system surface

`collect_cell_mbr_nearest_frontier_3d_optix` now accepts:

```python
sort_rows: bool = True
```

If `sort_rows=False` and the loaded backend does not export the v2 symbol, the
wrapper fails closed with a rebuild-required error. It does not silently fall
back to the old sorted symbol.

`cell_mbr_nearest_frontier_native_3d_optix_columns` now accepts:

```python
sort_rows: bool = True
```

and records:

```text
sort_rows
frontier_row_order = sorted_unique | native_unsorted
native_generic_symbol
```

### X-HD representative route

The X-HD route scripts now expose:

```text
--frontier-row-order sorted|native
```

`sorted` is the legacy control. `native` requests `sort_rows=False` for the
streaming X-HD route (`emit_pruned_rows=False`, `return_split_frontiers=False`).

## POD Validation

POD:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Build:

```text
cd /root/rtdl_goal5093
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc
```

Focused POD tests:

```text
python3 -m unittest \
  tests.goal5171_unsorted_native_frontier_rows_test \
  tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 22 tests OK
```

Local focused tests:

```text
py -m unittest \
  tests.goal5171_unsorted_native_frontier_rows_test \
  tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 25 tests OK
```

## Same-POD Full Public Res4 Evidence

Commands:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full --backend optix --validation-mode author-only \
  --rtdl-repeat-count 5 \
  --frontier-nearest-executor numba_parallel \
  --frontier-row-order sorted \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5171_sorted_frontier_rows_matrix_pod.json

python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full --backend optix --validation-mode author-only \
  --rtdl-repeat-count 5 \
  --frontier-nearest-executor numba_parallel \
  --frontier-row-order native \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5171_native_unsorted_frontier_rows_matrix_pod.json
```

Results:

| Route | Matched | Native Symbol | Row Order | Route Median | Total Median |
|---|---:|---|---|---:|---:|
| sorted control | true | `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2` | `sorted_unique` | 0.033758156 s | 0.074921824 s |
| native unsorted | true | `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2` | `native_unsorted` | 0.033091016 s | 0.073873185 s |

Delta:

```text
route median: 0.033758156 -> 0.033091016 s
absolute route improvement: ~0.000667 s
relative route improvement: ~1.98%
total median: 0.074921824 -> 0.073873185 s
absolute total improvement: ~0.001049 s
```

Direction subphase medians:

| Direction | Row Order | Frontier Rows | Nearest Continuation |
|---|---|---:|---:|
| A->B | sorted | 0.005131960 s | 0.003344528 s |
| A->B | native | 0.003724612 s | 0.004194587 s |
| B->A | sorted | 0.006028779 s | 0.003443353 s |
| B->A | native | 0.004374288 s | 0.004571781 s |

Interpretation:

- Native unsorted rows reduce the native frontier phase by about 1.4-1.7 ms per
  direction.
- Part of that saving moves into continuation grouping because the downstream
  grouped Numba continuation now receives native emission order instead of
  sorted rows.
- Net route improvement is real but small, about 2% on this full public res4
  representative case.

## Why This Is Generic

The new switch is named in terms of row ordering, not X-HD or Hausdorff. It is a
property of the generic cell-MBR nearest-frontier row producer:

```text
sort_rows=True  -> sorted_unique compatibility row table
sort_rows=False -> native_unsorted streaming row table
```

The route remains:

```text
generic grid cell-MBRs
generic native 3-D cell-MBR frontier rows
generic nearest-witness continuation
generic max-nearest reduction
```

No X-HD-specific primitive, author algorithm shortcut, or paper semantic is
added to RTDL core.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not authorize any author-vs-RTDL speedup/parity ratio.
- It does not prove native unsorted rows are always faster for all consumers.
- It does not remove the need for sorted+unique row tables where deterministic
  ordering or duplicate elimination is part of the consumer contract.

## Next Work

The route is now balanced across several small phases. The measured next work
should be selected from fresh evidence. Two likely directions:

1. If keeping the current streaming consumer, investigate whether continuation
   grouping can consume native row order more directly, so the removed native
   sort does not reappear downstream.
2. Otherwise, stop micro-optimizing this Level B representative route and send
   Goals5130-5171 as a consolidated review packet before more code.
