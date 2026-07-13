# Goal5212 All-Source No-Copy Selection Result

Date: 2026-07-09

## Verdict

```text
completed_all_source_no_copy_selection_fastpath__full_gate_total_moves
```

## Purpose

After Goal5211, the full-public Level-B route was much faster, but the
full-public subset-scaling runner still spent about `0.216s` in
`select_source_subset` even when:

```text
source_limits = all
```

That work was unnecessary. The runner selected every source index and then
materialized:

```text
points_a_full[np.asarray(source_indices), :]
```

For an all-source run, this is an avoidable full matrix copy.

## Implementation

Changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5207_explicit_route_warmup_protocol_test.py
```

New behavior:

```text
if source_limit == source_count:
    points_a_subset = points_a_full
    source_subset_materialized = false
    source_subset_selection_contract = all_source_no_copy_view
else:
    points_a_subset = points_a_full[index_array, :]
    source_subset_materialized = true
    source_subset_selection_contract = deterministic_indexed_subset_copy
```

The output still records deterministic `selected_indices_head` and
`selected_indices_tail`; it just no longer builds the full index list or copies
the source matrix for the all-source case.

## Validation

Local:

```text
py -m unittest \
  tests.goal5207_explicit_route_warmup_protocol_test \
  tests.goal5211_global_bound_early_break_contract_test

Ran 5 tests OK

py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  tests/goal5207_explicit_route_warmup_protocol_test.py

OK

git diff --check
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python -m unittest \
  tests.goal5207_explicit_route_warmup_protocol_test \
  tests.goal5211_global_bound_early_break_contract_test

Ran 5 tests OK
```

## POD Evidence

Workload:

```text
Level-B same-source public Stanford Dragon -> HappyBuddha
source_limits = all
grid_shape = 32,32,32
initial_state = local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
global_bound_early_break = true
author comparator = Goal5186 HDResult
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

Both runs:

```text
matched = true
author_abs_diff ~= 2.38e-9
source_subset_materialized = false
source_subset_selection_contract = all_source_no_copy_view
frontier_rows = 0
```

## Performance

Fresh no-warm:

| route | select_source_subset | route wall | case total | full total incl load | load_full_inputs |
|---|---:|---:|---:|---:|---:|
| Goal5211 global-bound fresh | 0.216s | 0.849s | 1.065s | 1.752s | 0.681s |
| Goal5212 all-source no-copy fresh | 0.000005s | 0.852s | 0.852s | 1.531s | 0.678s |

Explicit warm protocol:

| role | select_source_subset | route wall | case total | native total | OptiX launch |
|---|---:|---:|---:|---:|---:|
| warmup | 0.000005s | 0.842s | 0.842s | 0.269s | 0.038s |
| measured | 0.000007s | 0.288s | 0.288s | 0.061s | 0.039s |

Interpretation:

```text
This goal does not improve the route kernel itself.
It removes an app-runner full-source copy that made all-source case_total and
full total worse than necessary.
```

## Claim Boundary

Allowed:

```text
Goal5212 removes unnecessary all-source subset materialization in the X-HD
full-public runner. It improves full-public all-source gate wall time while
preserving the same route and author HDResult match.
```

Not authorized:

```text
full X-HD paper reproduction
exact paper dataset identity
author-vs-RTDL performance ratio
X-HD-specific RTDL primitive
native route speedup claim
using warm numbers as fresh headline
```

## Next Recommendation

Goal5211 and Goal5212 should be reviewed together:

- Goal5211 is the generic route/kernel improvement.
- Goal5212 is the app-owned full-public runner hygiene that prevents all-source
  selection from hiding the route improvement behind a full matrix copy.

After review, decide whether:

1. the X-HD Level-B route should default to `global_bound_early_break=True` for
   directed-HD/max-nearest runs; and
2. the current Level-B route is ready for a consolidated performance packet.
