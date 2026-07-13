# Goal5192 Native Inline-Nearest Telemetry Result

## Status

`implemented_review_pending`

Goal5192 adds optional diagnostic telemetry for the generic native 3-D
cell-MBR inline-nearest collector used by the X-HD Level-B full-public
Dragon/HappyBuddha route.

This is an accounting goal, not a speedup goal. The best performance number for
the route remains the no-telemetry route from Goal5191 / the Goal5192 control.

## Why This Goal Exists

Goal5191 made `frontier_rows=0` by raising the generic native inline-nearest
threshold to `max_inline_points=512`. That removed Python continuation from the
hot route, but it also exposed a measurement gap:

```text
total_candidate_distance_evaluations = 23,668,840
frontier_rows = 0
native frontier / inline-nearest collector ~= 2.00s
```

The evaluation count only covered the local-grid seed and remaining Python
continuation. It did not count native point-distance work performed inside the
OptiX any-hit payload for inline cells. That made the current native floor look
like unexplained overhead.

Goal5192 closes that accounting gap with optional native counters:

```text
inline_cell_hit_count
inline_point_evaluation_count
```

## Implementation

### Native OptiX ABI

Files changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
```

New exported symbol:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4
```

The v4 symbol is the existing v3 collector plus optional output pointers:

```text
uint64_t* inline_cell_hit_count_out
uint64_t* inline_point_eval_count_out
```

The counters are enabled only when all of the following are true:

```text
inline_nearest_enabled
collect_inline_stats
inline_cell_hit_count_out != nullptr
inline_point_eval_count_out != nullptr
```

Inside the any-hit inline-nearest branch:

```text
atomicAdd(inline_cell_hit_count, 1)
atomicAdd(inline_point_eval_count, cell.point_count)
```

Existing v1/v2/v3 call sites pass null pointers and keep their prior behavior.

### Python RTDL Surface

Files changed:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
```

New optional argument:

```python
collect_inline_stats: bool = False
```

The option is fail-closed:

```text
collect_inline_stats=True requires inline_nearest=True
v4 native symbol must exist in the loaded OptiX library
```

Returned metadata now includes:

```text
inline_stats_collected
inline_cell_hit_count
inline_point_evaluation_count
```

### X-HD Gate Runner

Files changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

New CLI flag:

```text
--collect-inline-stats
```

The flag is optional and diagnostic. It is not part of the fastest route.

## POD Validation

POD:

```text
host = 213.173.108.24
port = 13502
workspace = /root/rtdl_goal5093
```

Build:

```text
make build-optix
```

Symbol check:

```text
nm -D build/librtdl_optix.so | grep rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4
00000000000dad50 T rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4
```

Focused POD tests:

```text
python3 -m unittest \
  tests.goal5192_inline_nearest_telemetry_test \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5190_grid_branch_bound_seed_test
```

Result:

```text
Ran 16 tests in 10.864s
OK
```

## Full-Public Level-B Evidence

Input:

```text
source = public Stanford Dragon, 437645 points
target = public Stanford HappyBuddha, 543652 points
author_hd_result = 0.12572988867759705
```

Both control and telemetry runs use:

```text
backend = optix
grid_shape = 32,32,32
source_limits = all
initial_state = local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
frontier_row_capacity = 0
skip_exact_oracle = true
```

The explicit zero frontier capacity is fail-closed: the run would fail if the
native inline-nearest collector emitted any frontier rows.

### No-Telemetry Control

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_no_telemetry_control_goal5192_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
author_abs_diff = 2.3848857610975216e-09
route_wall = 3.7021561563014984s
case_total = 3.8899370208382607s
direction_total = 3.374729707837105s
frontier_rows = 0
inline_stats_collected = false
total_candidate_distance_evaluations = 23668840
```

Subphases:

```text
initial_state_seed = 0.8985391035676003s
frontier_rows / native inline-nearest collector = 2.0371295884251595s
nearest_continuation = 0.0164734348654747s
max_nearest_reduction = 0.07165445387363434s
```

### Telemetry Run

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_telemetry_goal5192_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
author_abs_diff = 2.3848857610975216e-09
route_wall = 3.8734402880072594s
case_total = 4.060122989118099s
direction_total = 3.5476405322551727s
frontier_rows = 0
inline_stats_collected = true
inline_cell_hit_count = 12003138
inline_point_evaluation_count = 1242677739
total_candidate_distance_evaluations = 23668840
```

Subphases:

```text
initial_state_seed = 0.9370666369795799s
frontier_rows / native inline-nearest collector = 2.176773577928543s
nearest_continuation = 0.016389623284339905s
max_nearest_reduction = 0.07230885326862335s
```

## Interpretation

Goal5192 changes the performance diagnosis:

```text
old visible candidate distance evaluations = 23,668,840
new native inline point evaluations        = 1,242,677,739
```

The native inline-nearest collector is not mostly fixed overhead. It is doing
about `1.24B` point-distance evaluations inside OptiX any-hit payloads on this
full-public Level-B route.

This explains the remaining native collector floor after Goal5191:

```text
frontier_rows = 0
nearest_continuation ~= 0.016s
native inline-nearest collector ~= 2.0s
```

## Claim Boundary

Authorized claims:

- optional native telemetry for generic 3-D cell-MBR inline-nearest collection;
- v4 native symbol exists and POD tests pass;
- the telemetry run matched the author HDResult;
- the full-public Level-B route performs about `1.24B` native inline point
  evaluations at `max_inline_points=512`.

Not authorized:

- no author-vs-RTDL performance ratio;
- no author performance parity;
- no exact paper dataset reproduction;
- no full X-HD paper reproduction;
- no claim that telemetry route time is the fastest route time;
- no claim that native inline-nearest telemetry is free.

The no-telemetry control remains the appropriate performance route. The
telemetry artifact is an accounting artifact.

## Next Work

The next route target, if optimization continues, is now sharper:

```text
reduce native inline point evaluations or make the native inline-nearest
collector faster, without adding X-HD-specific shortcuts.
```

Candidate generic directions:

- better seed or tighter generic upper bounds that reduce inline cell hits;
- more selective generic cell ordering / cell-neighbor pruning;
- native payload-level reduction improvements;
- stop route optimization and send Goals5130-5192 for review before further
  work.
