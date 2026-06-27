# Handoff: Goal3313 Claude Review Of Goal3312 Batch Graph Negative Probe

Date: 2026-06-04
Repo: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`
Branch: `main`
Expected output: `docs/reviews/goal3313_claude_review_goal3312_batch_graph_negative_probe_2026-06-04.md`

## Task

Please perform an independent Claude review of Goal3312. Goal3312 attempted a replayable CUDA graph handle for the prepared point/closed-shape batch scalar-count path, found that graph replay returned zeros on the A5000 smoke, and hardened the Python wrapper to fail closed by validating replay against the trusted batch-count path before returning a graph handle.

## Files To Inspect

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal3312_prepared_point_batch_graph_count_test.py`
- `docs/reports/goal3312_prepared_point_batch_graph_negative_probe_2026-06-04.md`
- `docs/reports/goal3312_batch_graph_replay_negative_probe_2026-06-04.json`
- `docs/reports/goal3310_prepared_point_batch_scalar_count_2026-06-04.md`
- `docs/reviews/goal3311_claude_review_goal3310_batch_scalar_count_2026-06-04.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does the graph surface remain generic and app-agnostic despite being motivated by the RayJoin PIP benchmark?
2. Does the implementation fail closed, both structurally and in the Python wrapper, when graph replay returns incorrect counts?
3. Does the report accurately record the negative result (`exact=2`, trusted single/batch counts `2`, graph replay zeros, wrapper failure) without turning it into performance evidence?
4. Are claim boundaries, timing mode labels, commit hash, pod build/test evidence, and future-version notes consistent?
5. Should this graph surface remain as a guarded experimental/negative path, or should it be quarantined further before any public surface is exposed?
6. Is the recommended next direction sound: focus on a compact generic closed-shape predicate-count primitive instead of claiming CUDA graph replay success?

## Required Output

Write a Markdown review at:

`docs/reviews/goal3313_claude_review_goal3312_batch_graph_negative_probe_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Lead with findings by severity. Do not authorize release, public speedup claims, RayJoin paper reproduction claims, RTDL-beats-RayJoin claims, broad RT-core speedup claims, true-zero-copy claims, or app-specific native-engine direction.
