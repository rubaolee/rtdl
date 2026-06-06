# Goal3645 Prepared Segment Left-Set Sparse Count Route

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3643 isolated the important segment-pair bottleneck: the generic
RTDL/OptiX sparse count route is fast once the left side is already packed, but
one-shot calls still pay left-side packing and upload. Goal3645 turns that
diagnostic into a real reusable runtime feature.

New generic OptiX ABI surface:

- `rtdl_optix_prepare_segment_pair_left_set`
- `rtdl_optix_prepared_segment_pair_left_id_count_prepared_left_device_columns`
- `rtdl_optix_destroy_prepared_segment_pair_left_set`

Python surface:

- `prepare_segment_pair_left_set_optix(left_segments)`
- `PreparedOptixSegmentPairIntersection.left_id_count_prepared_left_device_columns(...)`

This is still app-agnostic. It prepares a left segment set and reuses it with a
prepared right segment-pair index to produce grouped count columns by left id.
No RayJoin vocabulary or app logic enters the native engine.

## Artifact

Machine artifact:

- `docs/reports/goal3645_segment_pair_prepared_left_sparse_a5000/summary.json`

Pod source state:

- source commit: `1276d8d6`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)
- runner flag: `prepare_left_set_for_optix == true`
- output cap: `max_counts_output == 4096`

## Correctness

All same-contract counts match the analytic sparse-grid reference and the CuPy
dense baseline.

| Case | Pair Count | Expected Hits | OptiX Hits | Match |
| --- | ---: | ---: | ---: | --- |
| sparse_diagonal_grid_8192 | 67,108,864 | 8,192 | 8,192 | yes |
| sparse_diagonal_grid_16384 | 268,435,456 | 16,384 | 16,384 | yes |
| sparse_diagonal_grid_32768 | 1,073,741,824 | 32,768 | 32,768 | yes |

## Diagnostic Timings

These timings are diagnostic only. The comparison is the same sparse-grid
same-contract comparison used in Goals 3639 and 3643: the runner's CuPy dense
all-pairs strict-v0 kernel versus RTDL/OptiX's prepared segment-pair count
route.

| Case | CuPy Dense Kernel Sec | CuPy Total Sec | Prepared-Left Count Sec | Prepared-Left Build Sec | CuPy Kernel / Prepared-Left Count |
| --- | ---: | ---: | ---: | ---: | ---: |
| sparse_diagonal_grid_8192 | 0.011594 | 0.018828 | 0.000275 | 0.008513 | 42.142x |
| sparse_diagonal_grid_16384 | 0.046331 | 0.048180 | 0.000319 | 0.017072 | 145.045x |
| sparse_diagonal_grid_32768 | 0.182643 | 0.188292 | 0.000430 | 0.029294 | 424.328x |

## Interpretation

This closes the immediate bottleneck found by Goal3643 for repeated sparse
segment-pair count workloads:

- the left segment set can now be uploaded/prepared once;
- repeated count calls avoid both Python repacking and native left upload;
- the measured hot count route becomes substantially faster than the dense CuPy
  same-contract kernel in the large sparse regime;
- the one-time prepared-left build cost remains visible and must be amortized
  by reuse.

The next performance question is not "can the count route be fast?" It can. The
next question is how high-level benchmark apps expose this prepared-left reuse
without hiding execution plans or turning app policy into engine logic.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- treating prepared-left hot-route timing as one-shot app-wall timing.

The accepted claim is narrow: RTDL now has a generic reusable left-side segment
set handle for prepared segment-pair grouped-count columns, and A5000 evidence
shows it removes the repeated left-upload bottleneck for large sparse
same-contract diagnostics.
