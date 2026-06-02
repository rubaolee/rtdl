# Handoff: Claude Review For Goal3042 Active-Frontier Hausdorff Performance

Please perform an independent read-only review of Goal3042.

## Repository

`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`

Main branch latest pushed commit to review:

```text
c10301b7 Goal3042 record active frontier A4000 performance
```

## Context

The v2.6 Hausdorff lane had several negative or partial results:

- full nearest-witness row materialization was correct but slower;
- Numba argmax over device columns was correct but still not fast enough;
- the needed design direction was a device-resident active-set/candidate-frontier primitive.

Goal3042 adds a generic OptiX active-frontier nearest-witness reduction:

```text
rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d
```

The primitive must remain app-agnostic: point groups, threshold radius, active frontier, nearest witness, max-distance reduction. No Hausdorff/X-HD/app-specific native ABI or kernel names are allowed.

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/reports/goal3042_point_group_active_frontier_witness_selection_2026-06-02.md`
- `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json`
- `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02/*.json`
- `tests/goal3042_point_group_active_frontier_witness_selection_test.py`

## Evidence To Verify

Local focused gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3042_point_group_active_frontier_witness_selection_test tests.goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_test tests.goal3037_point_group_nearest_numba_argmax_a4000_pod_test
```

Pod evidence:

- Host: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000
- Driver: 580.159.03
- CUDA prefix: `/usr/local/cuda-12.8`
- OptiX prefix: `/root/vendor/optix-sdk`
- CuPy: 14.1.1 in `/root/.venvs/rtdl_goal3042/bin/python`

Timing summary to verify:

| Points | CuPy grouped-grid sec | Active-frontier RT sec | Active speedup vs CuPy |
| ---: | ---: | ---: | ---: |
| 4096 | 0.004776468 | 0.006584461 | 0.725x |
| 8192 | 0.008929983 | 0.011395584 | 0.784x |
| 16384 | 0.032289381 | 0.020904737 | 1.545x |
| 32768 | 0.079344464 | 0.038273932 | 2.073x |
| 65536 | 0.300481389 | 0.078558422 | 3.825x |
| 131072 | 1.101468301 | 0.168522497 | 6.536x |

All tested rows should match the exact reference.

## Review Questions

1. Does Goal3042 preserve the app-agnostic native-engine boundary?
2. Is the active-frontier method exact under the stated contract, and did the witness-index fix correctly map sorted BVH target IDs back to original input indices?
3. Are the artifact timings and speedup ratios computed correctly?
4. Is it fair to call this bounded internal positive A4000 evidence while still refusing public speedup/release/true-zero-copy claims?
5. What residual risks or next engineering steps should Codex handle before making any public Hausdorff RT-core performance claim?

## Required Output

Write your review to:

```text
docs/reviews/goal3043_claude_review_goal3042_active_frontier_perf_2026-06-02.md
```

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please keep the review read-only except for writing that review file.
