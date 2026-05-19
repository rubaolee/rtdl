# Handoff: Goal2381 Prepared 3D Neighbor Ranked Rows Review

Date: 2026-05-19

Please perform an independent read-only review of Goal2381.

Expected review outputs:

- Gemini: `docs/reviews/goal2382_gemini_review_goal2381_ranked_rows_2026-05-19.md`
- Claude: `docs/reviews/goal2383_claude_review_goal2381_ranked_rows_2026-05-19.md`

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2381_native_prepared_frn3d_ranked_rows_pod_runner.sh`
- `tests/goal2381_prepared_3d_neighbor_ranked_rows_test.py`
- `docs/reports/goal2381_prepared_3d_neighbor_ranked_rows_2026-05-19.md`
- `docs/reports/goal2381_native_prepared_frn3d_ranked_rows_pod/*.json`

## Review Questions

1. Does Goal2381 add a generic app-agnostic prepared fixed-radius 3D ranked-row continuation, rather than an RTNN- or app-specific native ABI?
2. Does the public surface preserve the Python/RTDL contract through `PreparedOptixFixedRadiusNeighbors3D.run_ranked_raw(...)`, `run_ranked(...)`, and `--result-mode ranked-raw` / `ranked-dict`?
3. Does the native row layout for `RtdlKnnNeighborRow` match the Python `ctypes` layout, including offsets and size?
4. Does the implementation correctly keep nearest-ranked rows by distance and neighbor-id tie-break, bounded by `k_max <= 64`?
5. Do the pod artifacts support the exact bounded claim in the report:
   - small correctness oracle `ok: true`;
   - no host exact-refine;
   - large 262,144-row case beats the old Goal2371 host-refined prepared row path;
   - small 65,536-row case is not claimed as a speedup because the clean rerun was setup/upload dominated?
6. Are the claim boundaries correct: no RTNN paper-equivalence claim, no RT-core neighbor-search claim, no arbitrary ANN claim, no broad nearest-neighbor acceleration claim?

## Known Evidence

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2381_prepared_3d_neighbor_ranked_rows_test \
  tests.goal2379_prepared_3d_neighbor_exact_rows_test \
  tests.goal2377_prepared_3d_neighbor_distance_summary_test \
  tests.goal2375_prepared_3d_neighbor_exact_count_summary_test \
  tests.goal2371_native_prepared_bounded_neighbor_3d_test \
  tests.goal2348_rtnn_v2_2_external_runner_test

Ran 23 tests in 0.541s
OK
```

Pod validation:

- Pod: `root@69.30.85.177 -p 22055`
- Checkout: `/root/work/rtdl_goal2368`
- Base commit: `459bcc6c` plus Goal2381 patch
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runner: `STEP_TIMEOUT_SECONDS=900 REPEAT=5 bash scripts/goal2381_native_prepared_frn3d_ranked_rows_pod_runner.sh`
- Exit: `REMOTE_EXIT:0`

Measured rows:

| Count | Goal2371 old prepared rows sec | Goal2379 exact unordered rows sec | Goal2381 ranked rows sec | Old/ranked | Ranked/exact |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.001928 | 0.012287 | 0.59x | 6.37x |
| 262,144 | 0.090302 | 0.030799 | 0.047824 | 1.89x | 1.55x |

## Requested Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Recommended baseline verdict if no issue is found: `accept-with-boundary`.

The correct boundary is that Goal2381 is a useful app-agnostic ranked-row
primitive with validated large-scale improvement over the old host-refined path,
but it is not a v2.2 release gate and it does not authorize broad RTNN or RT-core
claims.
