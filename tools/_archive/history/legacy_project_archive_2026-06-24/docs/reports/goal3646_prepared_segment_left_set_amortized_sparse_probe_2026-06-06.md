# Goal3646 Prepared Segment Left-Set Amortized Sparse Probe

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3645 added a reusable prepared-left segment-set handle. Goal3646 measures
the intended repeated-call use case: prepare the right segment-pair index once,
prepare/upload the left segment set once, then call the generic grouped count
route repeatedly.

This is a hot-route probe. It is not a one-shot app-wall benchmark.

## Artifact

Machine artifact:

- `docs/reports/goal3646_segment_pair_prepared_left_amortized_a5000/summary.json`

Pod source state:

- source commit: `6e061d83`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)
- repetitions per sparse case: `200`
- warmup: CuPy RawKernel and OptiX pipeline were warmed on a 256-case before
  measured rows

## Diagnostic Timings

The comparison is against the same CuPy dense all-pairs strict-v0 kernel used in
Goals 3639, 3643, and 3645. The prepared-left route validates source-row counts
for every repeated call.

| Case | CuPy Dense Kernel Sec | Prepared-Left Count Mean Sec | Prepared-Left Count Median Sec | CuPy Kernel / Count Mean | CuPy Kernel / Count Mean + Amortized Prepare |
| --- | ---: | ---: | ---: | ---: | ---: |
| sparse_diagonal_grid_8192 | 0.011653 | 0.000107 | 0.000103 | 109.250x | 57.587x |
| sparse_diagonal_grid_16384 | 0.046339 | 0.000100 | 0.000096 | 465.487x | 165.518x |
| sparse_diagonal_grid_32768 | 0.179146 | 0.000092 | 0.000089 | 1942.743x | 466.647x |

The measured run warms CuPy RawKernel compilation and the OptiX pipeline before
recording these rows. The preparation cost columns still include the
per-case right-index preparation and left-set upload.

## Interpretation

The result supports the engineering direction:

- repeated prepared-left count calls are stable at roughly `0.10 ms` on this
  A5000 diagnostic;
- the one-time prepared-left upload is visible but amortizes cleanly;
- the reusable handle turns Goal3643's "packed-left hot route" into a real
  runtime feature rather than a measurement trick;
- high-level benchmark code can now expose explicit prepared-left reuse for
  repeated sparse segment-pair count workloads.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- treating hot-route repeated-call timing as one-shot app-wall timing.

The accepted claim is narrow: RTDL has a generic prepared-left segment-set route
whose repeated sparse grouped-count calls are fast on A5000 evidence, with
preparation cost explicitly reported and amortized.
