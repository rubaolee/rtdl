# Handoff: Goal2384 Prepared 3D Neighbor Ranked Summary Review

Date: 2026-05-19

Please perform an independent read-only review of Goal2384.

Expected review outputs:

- Gemini: `docs/reviews/goal2385_gemini_review_goal2384_ranked_summary_2026-05-19.md`
- Claude: `docs/reviews/goal2386_claude_review_goal2384_ranked_summary_2026-05-19.md`

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2384_native_prepared_frn3d_ranked_summary_pod_runner.sh`
- `tests/goal2384_prepared_3d_neighbor_ranked_summary_test.py`
- `docs/reports/goal2384_prepared_3d_neighbor_ranked_summary_2026-05-19.md`
- `docs/reports/goal2384_native_prepared_frn3d_ranked_summary_pod/*.json`

## Review Questions

1. Does Goal2384 remain app-agnostic by exposing a prepared fixed-radius ranked-summary continuation, not an RTNN-specific native ABI?
2. Does the native `RtdlFixedRadiusRankedNeighborSummary` layout match the Python ctypes structure and the static assertions?
3. Does the ranked-summary kernel preserve nearest/kth/sum semantics for the bounded `k_max <= 64` top-K set?
4. Do the pod artifacts support the report:
   - small correctness oracle `ok: true`;
   - no host exact-refine;
   - one summary row per query;
   - large case improves over both Goal2381 ranked witness rows and Goal2371 old host-refined rows?
5. Are the claim boundaries correct: no RTNN paper-equivalence claim, no RT-core nearest-neighbor claim, no arbitrary ANN claim, no broad nearest-neighbor acceleration claim, no user-defined shader-extension claim?

## Known Evidence

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2384_prepared_3d_neighbor_ranked_summary_test \
  tests.goal2381_prepared_3d_neighbor_ranked_rows_test \
  tests.goal2379_prepared_3d_neighbor_exact_rows_test \
  tests.goal2377_prepared_3d_neighbor_distance_summary_test \
  tests.goal2375_prepared_3d_neighbor_exact_count_summary_test \
  tests.goal2371_native_prepared_bounded_neighbor_3d_test \
  tests.goal2348_rtnn_v2_2_external_runner_test

Ran 26 tests in 0.545s
OK
```

Pod validation:

- Pod: `root@69.30.85.177 -p 22055`
- Checkout: `/root/work/rtdl_goal2368`
- Base commit: `fd59109f` plus Goal2384 patch
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runner: `STEP_TIMEOUT_SECONDS=900 REPEAT=5 bash scripts/goal2384_native_prepared_frn3d_ranked_summary_pod_runner.sh`
- Exit: `REMOTE_EXIT:0`

Measured rows:

| Count | Goal2371 old prepared rows sec | Goal2381 ranked rows sec | Goal2384 ranked summary sec | Ranked rows / summary | Old rows / summary |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.012287 | 0.001526 | 8.05x | 4.77x |
| 262,144 | 0.090302 | 0.047824 | 0.008271 | 5.78x | 10.92x |

## Requested Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Recommended baseline verdict if no issue is found: `accept-with-boundary`.

The correct boundary is that Goal2384 validates a useful generic ranked-summary
continuation and shows why avoiding full row materialization matters, but it is
not a v2.2 release gate and does not authorize broad RTNN or RT-core claims.
