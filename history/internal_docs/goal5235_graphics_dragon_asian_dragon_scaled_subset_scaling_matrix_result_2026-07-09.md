# Goal5235 Graphics Dragon -> AsianDragon Scaled Subset Scaling Matrix Result

Date: 2026-07-09

## Verdict

```text
completed_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix__bounded_only
```

Goal5235 expands the Goal5234 scaled Dragon -> AsianDragon RTDL route from a
single 16-source subset to a bounded scaling matrix:

```text
source_limit = 16, 64, 256
target = full scaled AsianDragon public candidate, 3,609,600 points
source = deterministic evenly-spaced Dragon subsets
```

Every measured case matches an exact subset oracle with `route_abs_diff = 0.0`.

This is still bounded subset evidence. It is not all-source HDResult
reproduction, not Figure 6 reproduction, not exact paper input identity, and
not an author performance ratio.

## Matrix Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_2026-07-09.json
```

Input contract:

```text
Dragon public Stanford PLY
AsianDragon public Stanford PLY scaled by 1e-3
translate_each_input_to_min_bound = true
```

## Case Results

| source_limit | exact pair evals | matched | distance | route sec | exact sec | frontier rows | candidate evals |
|---:|---:|---|---:|---:|---:|---:|---:|
| 16 | 57,753,600 | true | 0.044985184486035196 | 2.7669001002795994 | 1.9203260000795126 | 9,090 | 163,249 |
| 64 | 231,014,400 | true | 0.06155463019045801 | 3.987872500438243 | 8.637364400085062 | 52,513 | 1,202,327 |
| 256 | 924,057,600 | true | 0.05981302471903363 | 7.3296191999688745 | 33.07700269995257 | 176,653 | 5,223,735 |

The 64 and 256 source cases are faster than the exact subset oracle:

```text
64-source route/exact ratio  = 0.4617
256-source route/exact ratio = 0.2216
```

These ratios are against a local exact subset oracle, not against the author
binary. They are not author-vs-RTDL performance claims.

## Capacity Diagnostic

Observed rows per source:

```text
16-source:  568.125
64-source:  820.515625
256-source: 690.05078125
```

Median-based all-source extrapolation:

```text
full source count = 437,645
estimated all-source frontier rows = 301,997,274
estimated all-source candidate distance evaluations = 8,221,756,249
```

This is diagnostic only, but it strongly suggests that a naive all-source
materialized frontier run is risky. The next all-source attempt should use an
explicit streaming/capacity strategy or a current POD/OptiX environment with
fail-closed capacity handling.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_graphics_dragon_asian_dragon_scaled_1e-3_subset16_numpy_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_1e-3_subset64_numpy_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_1e-3_subset256_numpy_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_2026-07-09.json
```

## Validation

The current route/input changes were validated with:

```text
py -m unittest \
  tests.goal5234_xhd_scaled_ply_candidate_test \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5178_xhd_priority_input_bridge_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5231_modelnet40_performance_matrix_test

Ran 15 tests in 1.866s
OK
```

Compile validation:

```text
py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_scaled_ply_candidate.py
```

Diff whitespace validation passed for the touched script/test files.

## POD Note

POD is reachable and has the current data plus author binary, but the available
RTDL source/build snapshot under `/tmp/rtdl_goal5144` is older than the current
X-HD route work. I did not mix current local scripts with an old remote RTDL
core and call the result current-RTDL evidence.

The next POD goal should either:

1. sync and rebuild the current RTDL route/native environment, or
2. explicitly label the run as an old-snapshot diagnostic.

## Claim Boundary

Allowed:

```text
The scaled Dragon -> AsianDragon public candidate has bounded RTDL subset
evidence at source limits 16, 64, and 256, and each case matches an exact
subset oracle.
```

Forbidden:

```text
RTDL all-source Dragon -> AsianDragon HDResult is reproduced.
Figure 6 is reproduced.
Exact paper input byte identity is proved.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next technical blocker is capacity/streaming for all-source scaled
Dragon -> AsianDragon. Recommended next goal:

```text
Goal5236: current-POD RTDL environment sync/rebuild + explicit-capacity
scaled Dragon -> AsianDragon POD/OptiX gate.
```

If current-POD sync is too expensive, the fallback is a local streaming
all-source route design that avoids materializing hundreds of millions of
frontier rows.
