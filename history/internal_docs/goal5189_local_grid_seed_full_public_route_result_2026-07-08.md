# Goal5189 Local-Grid Seed Full-Public Route Result

Date: 2026-07-08

## Verdict

`implemented_local_grid_seed_route_improves_full_public_rtdl_route__review_pending`

Goal5189 adds a generic local-grid-cell seed strategy and validates it on the
full public Stanford Dragon/HappyBuddha Level-B X-HD candidate. The new route
still matches the author `HDResult`, lowers same-POD RTDL route wall from about
`8.31s` to about `5.98s`, and cuts seed time from about `5.15s` to about
`0.90s`.

This is a route-local RTDL system improvement. It is not an author performance
ratio, not exact paper dataset reproduction, and not full paper reproduction.

## Implementation

### Generic RTDL helper

Added:

```text
src/rtdsl/partner_continuations.py
  seed_nearest_witness_from_local_grid_cell_numpy_columns(...)
```

The helper:

- consumes generic `point_grid_cell_mbrs_numpy_columns(...)` descriptors;
- uses a local occupied grid-cell search to find a deterministic seed cell;
- computes an exact nearest witness inside that seed cell;
- returns a valid nearest-state upper bound for later frontier refinement;
- is explicitly named as a local-grid seed, not as a nearest-MBR seed.

The helper metadata says:

```text
contract = generic_seed_nearest_witness_from_local_grid_cell
seed_quality = valid_upper_bound_not_nearest_cell_mbr
app_semantics = none
rt_core_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
```

This avoids the previous full scan over every nonempty tight cell MBR:

```text
Goal5187/nearest-MBR seed:
  cell_mbr_tests = 437645 * 6454 = 2824560830

Goal5189/local-grid seed:
  grid_cell_probes = 37335261
```

### Grid descriptor metadata

`point_grid_cell_mbrs_numpy_columns(...)` now carries app-neutral grid-domain
metadata needed by the local-grid seed:

```text
grid_shape
grid_lower_bounds
grid_upper_bounds
```

The existing tight per-cell MBR columns and compact/original cell-id contracts
remain unchanged.

### X-HD route wiring

`run_xhd_cell_mbr_frontier_route_gate.py` now accepts:

```text
--initial-state local-grid-cell
```

`run_xhd_full_public_subset_scaling_gate.py` forwards the same initial-state
choice. The default remains `nearest-cell-mbr`, so existing artifacts are not
silently reinterpreted.

## POD Evidence

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Both runs use the same full public Level-B candidate:

```text
source = Stanford Dragon, 437645 points
target = Stanford HappyBuddha, 543652 points
backend = optix
grid_shape = 32,32,32
direction = author-directed input1-to-input2
validation = author HDResult from Goal5186
exact all-source oracle = skipped
```

Author anchor:

```text
Goal5186 author HDResult = 0.12572988867759705
tolerance = 1e-6
```

## Same-POD Control: Nearest-MBR Seed

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_nearest_mbr_control_goal5189_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
route distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09

route_wall = 8.307917766273022 s
total = 10.974521778523922 s
load_full_inputs = 2.4809606596827507 s

initial_state_seed = 5.148780770599842 s
frontier_rows = 1.8993358761072159 s
nearest_continuation = 0.4632937088608742 s

frontier_row_count = 2052249
cell_mbr_tests = 2824560830
total_candidate_distance_evaluations = 342424979
```

## New Route: Local-Grid Seed

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_goal5189_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
route distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09

route_wall = 5.982383579015732 s
total = 8.77556024491787 s
load_full_inputs = 2.6060548275709152 s

initial_state_seed = 0.8984613716602325 s
frontier_rows = 2.2998608872294426 s
nearest_continuation = 2.0311837941408157 s

frontier_row_count = 7590188
grid_cell_probes = 37335261
total_candidate_distance_evaluations = 1109149179
```

## Delta

Same-POD route wall:

```text
nearest-MBR control = 8.307917766273022 s
local-grid seed     = 5.982383579015732 s
delta               = -2.32553418725729 s
relative            ~= 1.39x faster route wall
```

Phase movement:

```text
seed:          5.1488s -> 0.8985s   (-4.2503s)
frontier:      1.8993s -> 2.2999s   (+0.4005s)
continuation:  0.4633s -> 2.0312s   (+1.5679s)
```

The improvement is real but not free. Local-grid seed removes most seed work,
but it produces looser upper bounds, which increases frontier rows and
continuation candidate work. The net result is still faster on this full-public
Level-B route.

## Claim Boundary

Authorized:

- generic RTDL helper added;
- local-grid seed route matches author HDResult on the full public Level-B
  Dragon/HappyBuddha candidate;
- route-local same-POD control shows a lower RTDL route wall for this case;
- nearest-MBR seed remains available.

Not authorized:

- no author performance ratio;
- no author parity claim;
- no exact paper dataset reproduction claim;
- no full X-HD paper reproduction claim;
- no claim that local-grid seed is universally faster on every input;
- no claim that local-grid seed selects the nearest tight cell MBR.

## Validation

Local:

```text
py -m unittest \
  tests.goal5189_local_grid_seed_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test

Ran 16 tests in 1.436s
OK
```

POD:

```text
python3 -m unittest \
  tests.goal5189_local_grid_seed_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test

Ran 8 tests in 6.993s
OK
```

POD route gates:

```text
nearest-MBR control: matched=true
local-grid seed:     matched=true
```

## Next Work

The largest remaining route costs after local-grid seed are:

```text
frontier_rows ~= 2.30s
nearest_continuation ~= 2.03s
```

Because local-grid seed trades seed work for more frontier/continuation work,
the next decision should be profile-driven:

1. either keep local-grid seed as the full-public route strategy and attack the
   expanded frontier/continuation cost generically;
2. or design a stronger indexed seed that is still cheaper than nearest-MBR
   all-cell scan but tighter than first local occupied cell.

Any next step must remain generic RTDL system work and preserve the Goal5187 /
Goal5189 author HDResult match.
