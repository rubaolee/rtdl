# Goal5234 Graphics Dragon -> AsianDragon Scaled Author Gate Result

Date: 2026-07-09

## Verdict

```text
completed_graphics_dragon_asian_dragon_scaled_public_candidate_author_gate__level_b_only
```

Goal5234 resolves the large discrepancy discovered after Goal5233:

```text
raw public AsianDragon author HDResult = 52.453487396240234
paper-log Dragon -> AsianDragon HDResult = 0.06536811590194702
```

The discrepancy was not an author-binary failure. It was an input-coordinate
scale contract. The author paper-branch logs report AsianDragon MBR extents at
roughly `1e-3` of the public Stanford XYZRGB coordinates.

## Evidence

Author paper-branch log MBR for `asian_dragon.ply`:

```text
x extent = 0.20174401998519897
y extent = 0.11202627420425415
z extent = 0.13420195877552032
```

Raw public Stanford AsianDragon author run MBR:

```text
x extent = 201.7435302734375
y extent = 112.0262680053711
z extent = 134.2019500732422
```

The ratio is approximately `1000x`.

Goal5234 therefore prepares an app-owned scaled candidate:

```text
input:  Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon.ply
output: Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply
scale:  0.001
format: binary_big_endian 1.0
faces_preserved: false
```

Preparation summary:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_asian_dragon_scaled_1e-3_candidate_summary_2026-07-09.json
```

Scaled extents:

```text
x = 0.20174352264404297
y = 0.1120262680053711
z = 0.1342019500732422
```

These match the paper-log MBR extents within float32/public-file rounding.

## Author POD Runs

Raw public candidate:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_raw_public_gate_summary_2026-07-09.json
```

Result:

```text
author_hd_result = 52.453487396240234
paper_log_hd_result = 0.06536811590194702
paper_log_min_abs_diff = 52.38811928033829
matched = false
author_running_avg_time_ms = 20.281799999999997
```

Scaled public candidate:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_scaled_1e-3_public_gate_summary_2026-07-09.json
```

Result:

```text
author_hd_result = 0.06536787003278732
paper_log_hd_result = 0.06536811590194702
paper_log_min_abs_diff = 2.4586915969848633e-07
tolerance = 1e-6
matched = true
author_running_avg_time_ms = 82.5102
author_input_point_counts = [437645, 3609600]
```

This proves the deterministic public candidate transform recovers the author
paper-log HDResult for Dragon -> AsianDragon within the existing Level-B
tolerance. It still does not prove byte-identical paper input files.

## RTDL Bounded Subset Gate Under The Same Scaled Contract

Route artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_graphics_dragon_asian_dragon_scaled_1e-3_subset16_numpy_2026-07-09.json
```

Result:

```text
source points = 437645
target points = 3609600
source_limit = 16
exact pair evaluations = 57753600
all_matched = true
route_abs_diff = 0.0
```

Route and exact subset oracle:

```text
RTDL route distance = 0.044985184486035196
RTDL route source_id = 0
RTDL route target_id = 1695001

Exact subset distance = 0.044985184486035196
Exact subset source_id = 0
Exact subset target_id = 1695001
```

Timing from this local bounded run:

```text
exact_subset_reference_sec = 1.9203260000795126
rtdl_route_wall_sec = 2.7669001002795994
max_frontier_rows = 9090
```

This is a correctness gate. It is not a performance win; RTDL remains slower
than the exact subset oracle in this small bounded run.

## Code Changes

New app-owned preparation script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_scaled_ply_candidate.py
```

Related generalized route/author gate support:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
```

New focused test:

```text
tests/goal5234_xhd_scaled_ply_candidate_test.py
```

## Validation

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

Diff whitespace validation:

```text
git diff --check -- \
  Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_scaled_ply_candidate.py \
  tests/goal5205_fast_ascii_ply_matrix_loader_test.py \
  tests/goal5178_xhd_priority_input_bridge_test.py \
  tests/goal5181_xhd_full_public_subset_scaling_gate_test.py \
  tests/goal5234_xhd_scaled_ply_candidate_test.py
```

No whitespace errors.

## Claim Boundary

Allowed:

```text
For Dragon -> AsianDragon, the public Stanford AsianDragon file must be scaled
by 1e-3 to match the paper-branch input coordinate scale. Under that app-owned
transform, author hd_exec reproduces the paper-log HDResult within 1e-6, and
RTDL matches an exact 16-source subset oracle under the same scaled contract.
```

Forbidden:

```text
Exact paper input byte identity is proved.
Figure 6 is reproduced.
RTDL all-source Dragon -> AsianDragon HDResult is reproduced.
RTDL is faster than author or exact code.
Author-vs-RTDL performance parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next useful goal should run the RTDL all-source route against the scaled
Dragon -> AsianDragon candidate, or first run a larger bounded POD/OptiX
subset if all-source capacity is uncertain.

The author side is now known:

```text
paper-log HDResult = 0.06536811590194702
scaled-public author HDResult = 0.06536787003278732
```

The remaining work for this target is therefore RTDL all-source execution and
phase/performance accounting under the scaled input contract.
