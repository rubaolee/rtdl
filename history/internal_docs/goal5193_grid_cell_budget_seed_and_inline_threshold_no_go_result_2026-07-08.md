# Goal5193 Grid-Cell-Budget Seed And Inline Threshold No-Go Result

## Status

`implemented_review_pending__no_go_for_current_default_route`

Goal5193 tested two generic attempts to reduce the native inline-nearest floor
identified by Goal5192:

1. a new generic bounded grid-cell seed strategy;
2. intermediate inline-nearest thresholds between the earlier `256` and `512`
   sweep points.

Both preserve correctness on the full-public Level-B Dragon/HappyBuddha route,
but neither improves the current best route. The current default should remain:

```text
local-grid-cell seed + max_inline_points=512 + empty-frontier passthrough
```

## Motivation

Goal5192 showed that the `max_inline_points=512` route performs:

```text
inline_cell_hit_count = 12003138
inline_point_evaluation_count = 1242677739
```

The natural hypothesis was:

```text
tighten the current-best seed cheaply -> reduce native inline cell hits and
point-distance evaluations -> lower route wall time
```

Goal5190 had already proved that the complete grid branch-bound seed is too
expensive. Goal5193 therefore tried a middle strategy.

## Implementation

### Generic RTDL Helper

Files changed:

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
```

New helper:

```python
seed_nearest_witness_from_grid_cell_budget_numpy_columns(...)
```

Contract:

```text
generic_seed_nearest_witness_from_grid_cell_budget
```

Behavior:

- scans nearby occupied grid cells in deterministic grid-shell order;
- evaluates exact point distances inside at most
  `max_scanned_cells_per_query` occupied cells;
- returns a valid nearest-witness upper-bound seed;
- does not promise exact nearest-neighbor completion;
- uses app-neutral metadata (`app_semantics = none`).

The helper is intentionally between:

```text
local-grid-cell seed: cheap, loose
grid-branch-bound seed: tighter, expensive
```

### X-HD Runner Hook

Files changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

New route option:

```text
--initial-state grid-cell-budget
--seed-cell-budget <N>
```

Existing route defaults are unchanged.

### Tests

New test:

```text
tests/goal5193_grid_cell_budget_seed_test.py
```

Validation:

```text
py -m unittest \
  tests.goal5193_grid_cell_budget_seed_test \
  tests.goal5192_inline_nearest_telemetry_test \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5190_grid_branch_bound_seed_test
```

Local result:

```text
Ran 20 tests in 1.697s
OK
```

POD result:

```text
Ran 20 tests in 16.753s
OK
```

## POD Route Evidence

POD:

```text
host = 213.173.108.24
port = 13502
workspace = /root/rtdl_goal5093
```

Input:

```text
source = public Stanford Dragon, 437645 points
target = public Stanford HappyBuddha, 543652 points
author_hd_result = 0.12572988867759705
```

All runs:

```text
backend = optix
grid_shape = 32,32,32
source_limits = all
frontier_inline_nearest = true
skip_exact_oracle = true
matched = true
author_abs_diff ~= 2.38e-9
```

## Result 1: Grid-Cell-Budget Seed Is Not A Win

Comparison against the no-telemetry local-grid control:

```text
local-grid seed, inline512:
  route_wall = 3.7021561563014984s
  seed = 0.8985391035676003s
  frontier/native inline = 2.0371295884251595s
  seed_candidate_evaluations = 23668840
  frontier_rows = 0

grid-cell-budget=1, inline512:
  route_wall = 3.7161583453416824s
  seed = 0.695143073797226s
  frontier/native inline = 2.25310018658638s
  seed_candidate_evaluations = 32610887
  frontier_rows = 0
```

Budget 1 makes the seed phase cheaper but makes the native inline-nearest phase
more expensive. Net result: slightly slower than the current best control.

Telemetry explains why:

```text
local-grid telemetry:
  inline_cell_hit_count = 12003138
  inline_point_evaluation_count = 1242677739

grid-cell-budget=1 telemetry:
  inline_cell_hit_count = 20880543
  inline_point_evaluation_count = 2180127350
```

Budget 1 does not reduce native work. It lowers seed cost by choosing the first
bounded nearby occupied cell more cheaply, but it produces a looser seed and
increases native inline point evaluations.

Larger budgets reduce inline work only by spending too much seed time:

```text
grid-cell-budget=2 telemetry:
  route_wall = 8.232472009956837s
  seed = 1.1890686824917793s
  frontier/native inline = 6.103091984987259s
  seed_candidate_evaluations = 71730021
  inline_point_evaluation_count = 1743640481

grid-cell-budget=4 telemetry:
  route_wall = 7.764865949749947s
  seed = 1.9581187218427658s
  frontier/native inline = 4.96023341268301s
  seed_candidate_evaluations = 149519540
  inline_point_evaluation_count = 1354592850

grid-cell-budget=8 telemetry:
  route_wall = 8.141546063125134s
  seed = 2.2504488229751587s
  frontier/native inline = 5.117784634232521s
  seed_candidate_evaluations = 288125764
  inline_point_evaluation_count = 926382080
```

Conclusion:

```text
grid-cell-budget is generic and correct, but it should not replace local-grid
for the current full-public X-HD Level-B route.
```

## Result 2: Intermediate Inline Thresholds Do Not Beat 512

Goal5191 measured 256 and 512. Goal5193 filled in 320/384/448.

```text
inline256:
  route_wall = 4.027367681264877s
  frontier_rows = 505884
  frontier/native inline = 2.0159496143460274s
  nearest_continuation = 0.33656495064496994s
  continuation_candidate_evaluations = 161142983

inline320:
  route_wall = 7.7756113037467s
  frontier_rows = 201741
  frontier/native inline = 5.244287349283695s
  nearest_continuation = 0.2387094646692276s
  continuation_candidate_evaluations = 75262542

inline384:
  route_wall = 7.743091121315956s
  frontier_rows = 77360
  frontier/native inline = 5.144941918551922s
  nearest_continuation = 0.21509110182523727s
  continuation_candidate_evaluations = 32369692

inline448:
  route_wall = 7.730557970702648s
  frontier_rows = 13469
  frontier/native inline = 5.1964471861720085s
  nearest_continuation = 0.1981384977698326s
  continuation_candidate_evaluations = 6516820

inline512 + empty-frontier passthrough:
  route_wall = 3.647909864783287s
  frontier_rows = 0
  frontier/native inline = 2.0016997531056404s
  nearest_continuation = 0.016401365399360657s
  continuation_candidate_distance_evaluations = 0
```

The intermediate thresholds are substantially slower on this POD run. The
current best remains inline512.

## Artifacts

Grid-cell-budget artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget1_inline512_no_telemetry_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget1_inline512_telemetry_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget2_inline512_telemetry_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget4_inline512_telemetry_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget8_inline512_telemetry_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
```

Inline-threshold artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline320_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline384_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline448_goal5193_graphics_dragon_happy_buddha_2026-07-08.json
```

## Claim Boundary

Authorized claims:

- `seed_nearest_witness_from_grid_cell_budget_numpy_columns` is a generic
  bounded grid-cell seed helper;
- the helper passes focused local and POD tests;
- full-public Level-B route gates with the new seed matched author HDResult;
- the new seed and intermediate inline thresholds do not improve the current
  best route.

Not authorized:

- no author-vs-RTDL performance ratio;
- no author performance parity;
- no exact paper dataset reproduction;
- no full X-HD paper reproduction;
- no claim that grid-cell-budget should become the default route;
- no claim that intermediate inline thresholds beat inline512.

## Decision

Goal5193 should close as a measured no-go for this route:

```text
current_default = local-grid-cell + inline512 + empty-frontier passthrough
```

If route optimization continues, the next target should not be another
seed-threshold guess. Goal5192 and Goal5193 together suggest that the remaining
hard problem is deeper native inline-nearest collector efficiency or a more
substantial generic spatial index / traversal strategy.
