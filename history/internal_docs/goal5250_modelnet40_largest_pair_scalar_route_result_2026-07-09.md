# Goal5250 - ModelNet40 Largest-Pair Scalar Route Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_largest_unique_pair_scalar_route__matched_author
```

Goal5250 runs the current scalar route on the largest unique ModelNet40 pair
identified by the existing paper-log selection policy.

This complements Goal5249:

```text
Goal5249 = 10-category small/medium batch coverage
Goal5250 = largest-pair scale stress check
```

## Input

Selected pair:

```text
ModelNet40/airplane/train/airplane_0396.off
ModelNet40/airplane/train/airplane_0050.off
```

Point counts:

```text
input1 points = 439,910
input2 points = 2,286,376
total points  = 2,726,286
```

Author paper-log contract:

```text
algorithm = Hybrid
HDResult  = 0.1137629821896553
normalize = true
translate = 0.0
type      = Float
```

RTDL preprocessing:

```text
normalize_each_input_to_author_float32_unit_box
```

## Route

The same scalar route as Goal5247 / Goal5248:

```text
--grid-shape 96,60,72
--initial-state local-grid-cell
--local-grid-seed-executor native_cuda
--grid-cell-builder native_cuda
--frontier-inline-nearest
--global-bound-early-break
--frontier-row-order native
--direction-mode directed-a-to-b
--validation-mode author-only
```

## Evidence

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_fixed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_fixed_artifacts_2026-07-09.tar.gz
```

## Result

```text
selected_count = 1
matched_case_count = 1
failed_case_count = 0
all_cases_matched = true
```

Correctness:

```text
author_hd_result = 0.1137629821896553
rtdl_distance    = 0.11376298378980212
author_abs_diff  = 1.6001468206017222e-09
tolerance        = 1e-6
```

Performance:

```text
route_wall_sec = 1.0067468956112862
total_sec      = 7.567300736904144
```

Author denominators:

```text
author process_wall_sec   = 3.2632907927036285
author Running.AvgTime ms = 8.511
```

Internal route phases:

```text
direction_total      = 1.0066s class, fixed global-bound build
grid_cell_mbrs       = 0.33712945133447647
initial_state_seed   = 0.18214471638202667
frontier_rows        = 0.18475264310836792
nearest_continuation = 0.26268667727708817
max_nearest_reduction = 0.000865057110786438
```

Route statistics:

```text
frontier_row_count = 147,491
global_bound_early_break_count = 404,120 / 439,910 sources
total_candidate_distance_evaluations = 28,981,901
```

Critical caveat:

```text
per_source_witness_exact = false
```

This route is scalar `HDResult` exact for the author comparison, not exact
per-source witness output.

## Diagnostic Ratios

These are diagnostics only:

```text
RTDL route / author process wall       = 0.309x
RTDL total / author process wall       = 2.319x
RTDL route / author internal AvgTime   = 118.3x slower
```

The route wall is below author process wall on this case, but that is not an
author performance parity claim. The author internal `Running.AvgTime` remains
a much smaller denominator.

This report uses the fixed Goal5251 native global-bound implementation. The
pre-fix largest-pair run also matched, but the fixed evidence is the
authoritative one because Goal5251 found and repaired an unsafe global-bound
publish path.

## Claim Boundary

Allowed:

```text
The current scalar route matched author HDResult on the largest selected
ModelNet40 unique pair, with route wall about 1.00s on the current POD.
```

Forbidden:

```text
full X-HD paper reproduction
all ModelNet40 scalar route coverage
exact per-source witnesses
exact paper byte-input identity
Figure reproduction
author internal Running.AvgTime parity
speedup/parity claim
```

## Next Step

Send Goal5250 with Goal5249 for strict review. Together they provide:

```text
Goal5249: 10-category batch coverage
Goal5250: largest-pair scale stress coverage
```

They strengthen ModelNet40 scalar route evidence, but do not close the full
paper reproduction objective.
