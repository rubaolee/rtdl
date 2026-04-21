# Goal 717: Embree Prepared Fixed-Radius Summary Optimization

Date: 2026-04-21

## Verdict

ACCEPT for local implementation and focused correctness validation.

This goal adds a prepared Embree execution path for the v0.9.x fixed-radius count-threshold primitive used by the outlier and DBSCAN-style apps. The prepared path builds the Embree point-query scene once for the search-point set, then reuses that BVH for repeated query batches.

## Change Summary

- Added native Embree opaque handle API:
  - `rtdl_embree_fixed_radius_count_threshold_2d_create`
  - `rtdl_embree_fixed_radius_count_threshold_2d_run`
  - `rtdl_embree_fixed_radius_count_threshold_2d_destroy`
- Added Python API:
  - `rt.prepare_embree_fixed_radius_count_threshold_2d(search_points)`
  - `rt.PreparedEmbreeFixedRadiusCountThreshold2D`
- Preserved the existing one-shot API:
  - `rt.fixed_radius_count_threshold_2d_embree(...)`
- Added focused tests:
  - `tests/goal717_embree_prepared_fixed_radius_summary_test.py`
- Added local perf harness:
  - `scripts/goal717_embree_prepared_summary_perf.py`

## Correctness Finding During Implementation

The focused prepared-path test exposed a real issue in the existing count-threshold callback: Embree point-query traversal can report a candidate primitive more than once, and the summary path did not deduplicate candidate point IDs. The older row-emitting fixed-radius path already used a `seen_neighbor_ids` set.

Fix applied:

- `FixedRadiusCountThresholdQueryState` now carries `seen_neighbor_ids`.
- The callback skips already-seen search point IDs before incrementing `neighbor_count`.
- Both one-shot and prepared summary paths now use the same dedupe rule.

This is a correctness fix, not just a performance change.

## Local Performance

Raw perf JSON:

`/Users/rl2025/rtdl_python_only/docs/reports/goal717_embree_prepared_fixed_radius_summary_perf_local_2026-04-21.json`

Environment:

- Host: `Rs-MacBook-Air.local`
- Platform: `macOS-26.3-arm64-arm-64bit-Mach-O`
- Embree: `4.4.0`
- Thread mode: `auto`, effective threads `10`

Prepared run-only speedup over one-shot summary:

| copies | points | outlier speedup | DBSCAN speedup |
|---:|---:|---:|---:|
| 512 | 4,096 | 1.73x | 1.72x |
| 2,048 | 16,384 | 1.67x | 1.66x |
| 8,192 | 65,536 | 1.50x | 1.45x |
| 32,768 | 262,144 | 1.49x | 1.33x |

Boundary:

- The speedup is for repeated prepared Embree summary runs over a reused search-point BVH.
- It excludes Python JSON formatting, oracle checks, and full app CLI output.
- Prepare time is reported separately in the JSON.
- This does not claim whole-app speedup until apps are wired to retain prepared handles across repeated requests.

## Tests

Passed:

```text
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/embree_runtime.py \
  src/rtdsl/__init__.py \
  scripts/goal717_embree_prepared_summary_perf.py \
  tests/goal717_embree_prepared_fixed_radius_summary_test.py

PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal715_embree_fixed_radius_summary_test \
  tests.goal714_embree_app_thread_perf_test
```

Result:

```text
Ran 7 tests in 0.025s
OK
```

## Current Status

Goal717 is a useful Embree runtime optimization, especially for server/app loops that reuse a fixed search dataset across many query batches. The public demo apps do not yet expose a persistent prepared-session CLI mode, so this goal should be treated as a runtime capability plus microbenchmark evidence, not a final whole-app performance claim.

## Review Status

- Codex implementation review: ACCEPT.
- Gemini 2.5 Flash Lite review: ACCEPT, saved at `/Users/rl2025/rtdl_python_only/docs/reports/goal717_gemini_flash_lite_review_2026-04-21.md`.
- Gemini 2.5 Flash attempt: blocked by model capacity 429.
- Claude attempt: blocked by account limit, reset reported as 2pm America/New_York.

Consensus status: 2-AI consensus achieved by Codex plus Gemini Flash Lite. Claude review is not included because the CLI returned a limit message.

Recommended next step:

- Wire prepared fixed-radius summary into app-level reusable session paths or a batch benchmark mode, then test on Linux and Windows with large scales and configured thread counts.
