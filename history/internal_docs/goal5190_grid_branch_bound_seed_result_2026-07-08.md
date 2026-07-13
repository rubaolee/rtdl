# Goal5190 Grid Branch-Bound Seed Result

Date: 2026-07-08

## Verdict

`implemented_grid_branch_bound_seed__matched_author__do_not_replace_local_grid_default`

Goal5190 adds a generic grid-branch-bound seed strategy and validates it on the
full public Stanford Dragon/HappyBuddha Level-B route. It still matches the
author HDResult, and it substantially tightens the seed compared with
Goal5189's local-grid seed. However, the tighter seed is too expensive on this
input and does **not** beat Goal5189's local-grid route wall.

This is useful system evidence, not the new default route strategy.

## Implementation

Added:

```text
src/rtdsl/partner_continuations.py
  seed_nearest_witness_from_grid_branch_bound_numpy_columns(...)
```

The helper:

- consumes generic grid/cell descriptors;
- expands grid shells around each query point;
- scans cells while a grid-cell AABB lower bound can still improve the current
  exact point witness;
- returns an exact nearest witness under the generic grid branch-bound search;
- is app-neutral and carries `app_semantics=none`.

Route wiring:

```text
--initial-state grid-branch-bound
```

was added alongside the existing:

```text
--initial-state nearest-cell-mbr
--initial-state local-grid-cell
```

The default remains `nearest-cell-mbr`; Goal5189/5190 strategies are explicit
route choices.

## POD Evidence

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Full public Level-B candidate:

```text
source = Stanford Dragon, 437645 points
target = Stanford HappyBuddha, 543652 points
author HDResult = 0.12572988867759705
tolerance = 1e-6
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_branch_bound_seed_goal5190_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
route distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09

route_wall = 7.713007375597954 s
total = 10.412064984440804 s

initial_state_seed = 4.602560572326183 s
frontier_rows = 1.903033010661602 s
nearest_continuation = 0.44787507504224777 s

frontier_row_count = 1811625
grid_cell_probes = 857447554
scanned_cell_count = 8885749
initial_candidate_distance_evaluations = 748013062
continuation_candidate_distance_evaluations = 251181631
total_candidate_distance_evaluations = 999194693
```

## Three-Way Same-POD Comparison

```text
nearest-MBR control:
  matched = true
  route_wall ~= 8.31s
  seed ~= 5.15s
  frontier_rows = 2052249

local-grid seed:
  matched = true
  route_wall ~= 5.98s
  seed ~= 0.90s
  frontier_rows = 7590188

grid-branch-bound seed:
  matched = true
  route_wall ~= 7.71s
  seed ~= 4.60s
  frontier_rows = 1811625
```

Interpretation:

- local-grid seed is loose but cheap, and currently wins route wall;
- grid-branch-bound seed is tighter and reduces frontier/continuation work, but
  spends too much time in seed search;
- nearest-MBR seed remains the old control and is still slower than both newer
  strategies on this POD run.

## Claim Boundary

Authorized:

- generic grid-branch-bound seed helper exists;
- full public Level-B route still matches author HDResult;
- grid-branch-bound is a useful measured strategy/control.

Not authorized:

- no author performance ratio;
- no author parity claim;
- no exact paper dataset reproduction claim;
- no full X-HD paper reproduction claim;
- no claim that grid-branch-bound should replace local-grid seed as the current
  full-public route strategy;
- no claim that this seed strategy is universally faster.

## Validation

Local:

```text
py -m unittest \
  tests.goal5190_grid_branch_bound_seed_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test

Ran 20 tests in 29.757s
OK
```

POD:

```text
python3 -m unittest \
  tests.goal5190_grid_branch_bound_seed_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test

Ran 12 tests in 12.258s
OK
```

POD route:

```text
grid-branch-bound full-public all-source route: matched=true
```

## Next Work

The current best route strategy remains Goal5189 local-grid seed. Goal5190
shows that simply tightening the seed can lose by shifting cost back into seed
search. The next useful work should therefore either:

1. attack local-grid's expanded frontier/continuation costs; or
2. design a bounded-shell hybrid that gets part of branch-bound's tightness
   without paying full branch-bound seed cost.

Do not replace Goal5189 as the default route strategy based on Goal5190 alone.
