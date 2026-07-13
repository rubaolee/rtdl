# Goal5196 - Local-Grid Dense Cell Lookup

## Status

`implemented_review_pending`

Goal5196 improves the generic grid-cell nearest-state seed family used by the
current X-HD Level-B route.

Before this goal, each local-grid shell probe used a binary search over
`original_cell_ids` to decide whether an encoded grid cell was occupied. On the
full-public Dragon/HappyBuddha route, the local-grid seed probes about
`37.3M` grid cells, so the repeated binary search was a visible cost.

Goal5196 adds an app-neutral dense grid-cell position table for grids whose
total cell count is below a configurable cap:

```text
encoded grid cell id -> compact cell row index, or -1 when empty
```

The affected public helpers are:

```text
seed_nearest_witness_from_local_grid_cell_numpy_columns
seed_nearest_witness_from_grid_cell_budget_numpy_columns
seed_nearest_witness_from_grid_branch_bound_numpy_columns
```

and it now records:

```text
cell_lookup_strategy = dense_grid_cell_position_table
dense_lookup_cell_capacity = <grid volume>
dense_lookup_max_cells = <configured cap>
```

If the grid volume exceeds `dense_lookup_max_cells`, the helper falls back to
the previous `binary_search_original_cell_ids` lookup. This keeps the change
generic and prevents unbounded dense-table allocation.

This is generic RTDL seed machinery, not an X-HD-specific primitive.

## Implementation

Files changed:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5196_local_grid_dense_lookup_test.py
```

The implementation only changes grid-cell seed lookup:

```text
if grid_volume <= dense_lookup_max_cells:
    build dense position table and use O(1) encoded-cell lookup
else:
    use previous binary search over original_cell_ids
```

The point-distance reduction inside selected seed cells, seed quality, and
tie-break behavior remain unchanged.

## Validation

Local focused tests:

```text
py -m unittest \
  tests.goal5196_local_grid_dense_lookup_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test
```

Result:

```text
Ran 12 tests in 13.187s
OK
```

Additional local route-wrapper tests:

```text
py -m unittest \
  tests.goal5196_local_grid_dense_lookup_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5188_xhd_full_public_phase_matrix_test
```

Result:

```text
Ran 11 tests in 4.518s
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
workspace = /root/rtdl_goal5093
```

POD focused tests:

```text
python -m unittest \
  tests.goal5196_local_grid_dense_lookup_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test
```

Result:

```text
Ran 12 tests in 5.649s
OK
```

After extending the same dense lookup to the grid-cell-budget and grid
branch-bound helpers, the seed-focused local and POD suites were rerun:

```text
local:
  Ran 17 tests in 40.354s
  OK

POD:
  Ran 17 tests in 17.397s
  OK
```

## Full-Public Level-B Evidence

Input:

```text
source = public Stanford Dragon, 437645 points
target = public Stanford HappyBuddha, 543652 points
author_hd_result = 0.12572988867759705
```

Route:

```text
backend = optix
grid_shape = 32,32,32
source_limits = all
initial_state = local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
frontier_row_capacity = 0
skip_exact_oracle = true
payload-current-best pruning = true
intersection-stage current-best pruning = true
```

Two POD full-public runs with the dense lookup matched the author HDResult:

```text
run1:
  matched = true
  route_wall = 2.275638982653618s
  seed = 0.5542371273040771s
  native frontier / inline = 0.9530893340706825s

final2:
  matched = true
  route_wall = 2.256376951932907s
  seed = 0.5546591281890869s
  native frontier / inline = 0.9403322637081146s
  cell_lookup_strategy = dense_grid_cell_position_table
  dense_lookup_cell_capacity = 32768
  dense_lookup_max_cells = 8000000
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_dense_lookup_final2_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
```

Additional dense-lookup seed strategy controls:

```text
grid-cell-budget=1:
  matched = true
  route_wall = 2.275814287364483s
  seed = 0.5519751682877541s
  native frontier / inline = 0.9643965065479279s
  cell_lookup_strategy = dense_grid_cell_position_table

grid-cell-budget=2:
  matched = true
  route_wall = 2.307225279510021s
  seed = 0.5810719877481461s
  native frontier / inline = 0.9617605730891228s
  cell_lookup_strategy = dense_grid_cell_position_table

grid-branch-bound:
  matched = true
  route_wall = 6.0384648740291595s
  seed = 4.328845039010048s
  native frontier / inline = 0.9473775625228882s
  cell_lookup_strategy = dense_grid_cell_position_table
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget1_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget2_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_branch_bound_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
```

Comparison against Goal5195 final metadata-confirmation run:

```text
Goal5195 final4:
  route_wall = 2.5525703504681587s
  seed = 0.855375275015831s
  native frontier / inline = 0.9321393966674805s

Goal5196 final2:
  route_wall = 2.256376951932907s
  seed = 0.5546591281890869s
  native frontier / inline = 0.9403322637081146s
```

Observed route-local delta:

```text
seed:       0.855s -> 0.555s  (~35% lower)
route_wall: 2.553s -> 2.256s  (~11.6% lower, ~1.13x)
```

The native frontier / inline phase is essentially unchanged, as expected; this
goal attacks the seed lookup path.

## Interpretation

Goal5196 confirms that the grid-cell seed family still had meaningful generic
lookup overhead after Goal5195. Replacing repeated binary searches with a dense
cell-position table reduces seed time without changing route semantics.

The wider seed strategy retest is also useful: dense lookup does not overturn
the earlier default-route decision. `grid-cell-budget=1` and `grid-cell-budget=2`
are close, but still slower than dense local-grid on this route; branch-bound
remains much slower because it probes about `857M` grid cells. The current
default remains dense local-grid.

The current route floor is now roughly:

```text
local-grid seed ~= 0.55s
native frontier / inline ~= 0.94s
grid cell MBRs ~= 0.18s
source/target columns ~= 0.13s
max-nearest reduction ~= 0.07s
route wall ~= 2.26s
```

This is Level-B same-source representative route evidence on public Stanford
inputs. It is not an author performance comparison.

## Claim Boundary

Authorized claims:

- local-grid seed now uses a generic dense grid-cell position table when safe;
- grid-cell-budget and grid-branch-bound seeds use the same dense lookup when safe;
- fallback to binary search remains available for oversized grids;
- local and POD focused tests pass;
- full-public Level-B Dragon/HappyBuddha route still matches author HDResult;
- observed route wall is about `2.26s`;
- observed seed phase is about `0.55s`.

Not authorized:

- no author-vs-RTDL performance ratio;
- no author performance parity;
- no exact paper dataset reproduction;
- no full X-HD paper reproduction;
- no claim that this implements the author X-HD RT-core algorithm;
- no X-HD-specific primitive or copied author implementation.

## Decision

Goal5196 should become the current default local-grid seed lookup behavior.

`grid-cell-budget` and `grid-branch-bound` remain optional / control seed
strategies, not the default route for this Level-B workload.

The next route-internal options are:

```text
1. attack the remaining native frontier / inline phase (~0.94s);
2. reduce grid-cell MBR / column setup / reduction overhead;
3. pause for external review and exact-dataset / paper-figure provenance work.
```

Further seed work should be justified against the new `~0.55s` seed profile
rather than the older `~0.85-0.92s` profile.
