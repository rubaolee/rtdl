# Goal5245 Native Grid-Branch-Bound Seed Result

Date: 2026-07-09

## Verdict

```text
completed_native_grid_branch_bound_seed_capability__performance_no_go
```

Goal5245 implemented and tested a generic native CUDA executor for the
`grid-branch-bound` nearest-witness seed, plus an explicit exact-seed frontier
skip path. The system capability works and remains app-neutral, but it is **not
the best X-HD route for the current Dragon -> scaled AsianDragon Level-B
workload**.

## What Changed

Generic system additions:

- Native CUDA helper:
  `rtdl_cuda_grid_branch_bound_nearest_seed_3d_precompiled`
- Public native symbol:
  `rtdl_optix_seed_nearest_witness_grid_branch_bound_3d`
- Python binding:
  `seed_nearest_witness_grid_branch_bound_3d_cuda`
- Partner executor option:
  `seed_nearest_witness_from_grid_branch_bound_numpy_columns(..., executor="native_cuda")`
- Route CLI option:
  `--grid-branch-bound-seed-executor native_cuda`
- Route CLI option:
  `--skip-frontier-if-exact-seed`

The route shortcut is deliberately explicit. It only bypasses the frontier
producer when the seed declares:

```text
seed_quality = exact_nearest_witness_under_grid_cell_branch_bound
```

The default route remains unchanged.

## POD Evidence

Workload:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
direction = directed-a-to-b
preprocessing = translate_each_input_to_min_bound
grid_shape = 96x60x72
author HDResult = 0.06536787003278732
tolerance = 1e-6
```

Downloaded evidence files:

```text
history/internal_docs/goal5245_probe_grid_branch_bound_numba_current_pod_2026-07-09.json
history/internal_docs/goal5245_native_grid_branch_bound_seed_pod_2026-07-09.json
history/internal_docs/goal5245_native_grid_branch_bound_seed_skip_frontier_pod_2026-07-09.json
history/internal_docs/goal5245_native_grid_branch_bound_seed_skip_frontier_input_stable_pod_2026-07-09.json
```

All runs matched the author rerun value:

```text
author_abs_diff = 2.3747470656587666e-09
matched = true
```

## Performance Table

| Route | direction_total | rtdl_route_sec | Main phase |
|---|---:|---:|---|
| Current best from Goal5244, input-stable + OptiX inline-nearest | 2.3042s | not re-run here | frontier/inline-nearest |
| Numba grid-branch-bound seed + frontier | 31.3390s | 31.3391s | seed 29.2512s |
| Native CUDA grid-branch-bound seed + frontier | 3.6386s | 3.6386s | seed 1.7870s + frontier 1.2036s |
| Native CUDA grid-branch-bound seed + exact-seed frontier skip | 2.4508s | 2.4509s | seed 1.8066s + grid prep 0.6081s |
| Native CUDA grid-branch-bound seed + skip + input-stable point order | 2.4748s | 2.4749s | seed 1.8211s + grid prep 0.6165s |

## Interpretation

The native CUDA executor is a real capability improvement over the Numba
branch-bound seed:

```text
31.3390s -> 2.4508s with exact-seed frontier skip
```

But it still loses to the current best route:

```text
current best ~= 2.3042s
native exact seed + skip ~= 2.4508s
```

The reason is structural. The exact branch-bound seed scans a very large number
of target points:

```text
initial_candidate_distance_evaluations = 2,140,080,898
initial_grid_cell_probes = 6,170,907,111
initial_scanned_cell_count = 9,562,888
```

Even as a native CUDA kernel, that exact seed costs about:

```text
native kernel_sec ~= 1.54s
initial_state_seed outer ~= 1.81s
```

By contrast, the current best OptiX inline-nearest route uses traversal-side
cell-MBR pruning and wins despite paying the frontier launch.

## What This Proves

- The native CUDA branch-bound seed symbol builds and runs on POD.
- The Python binding and partner executor route select the native path.
- The exact-seed frontier skip is valid for seeds that explicitly declare exact
  per-source witnesses.
- The route remains generic: grid branch-bound nearest witness, not X-HD or
  Hausdorff-specific logic.
- Correctness is preserved for the representative Dragon -> scaled AsianDragon
  same-source workload.

## What This Does Not Prove

- It does not improve the current best X-HD Level-B route.
- It does not authorize replacing the Goal5244 best route.
- It does not prove full X-HD paper reproduction.
- It does not prove paper-log byte-input identity.
- It does not prove author internal `Running.AvgTime` parity.

## Recommendation

Do **not** adopt native grid-branch-bound seed as the default X-HD route for the
current workload.

Keep it as an app-neutral experimental system capability behind explicit
selection:

```text
--initial-state grid-branch-bound
--grid-branch-bound-seed-executor native_cuda
--skip-frontier-if-exact-seed
```

The next performance mountain is not more app-level grid shape tuning or this
exact seed. The remaining work is to design a stronger generic prepared spatial
index / nearest traversal strategy that avoids both:

```text
frontier OptiX launch ~= 1.17s
exact seed scan ~= 2.14B point-distance evaluations
```

## Verification

Local:

```text
py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py tests/goal5245_native_grid_branch_bound_seed_test.py
py -m unittest tests.goal5245_native_grid_branch_bound_seed_test tests.goal5190_grid_branch_bound_seed_test tests.goal5200_native_local_grid_seed_test
```

POD:

```text
make build-optix
python3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
python3 -m unittest tests.goal5245_native_grid_branch_bound_seed_test
```

POD test result:

```text
Ran 4 tests in 6.319s
OK
```
