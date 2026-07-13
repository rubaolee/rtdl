# Goal5183 - X-HD POD/OptiX Explicit Capacity Gate Result

Date: 2026-07-08

## Status

```text
completed_pod_optix_explicit_capacity_bounded_subset_gate__all_source_pending
```

Goal5183 moves the Goal5182 explicit-capacity bounded subset gate from local
NumPy readiness to a CUDA/OptiX POD run.

It validates that the scalable X-HD Level-B route can run against the full
public HappyBuddha target using the generic native OptiX 3-D cell-MBR frontier
producer with an explicit fail-closed row capacity.

It does **not** claim:

- all-source full public Dragon/HappyBuddha completion;
- exact paper dataset identity;
- paper figure reproduction;
- denominator-aligned author-vs-RTDL speedup;
- author performance parity;
- full X-HD paper reproduction.

## POD Evidence

Preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD command used the project wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Remote working directory:

```text
/root/rtdl_goal5093
```

Before the run, the full public Stanford PLY files and updated route scripts
were synchronized to the POD.

## Artifact

Downloaded artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_explicit_capacity_optix_goal5183_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.full_public_subset_scaling_gate.v1
```

Run:

```text
goal: Goal5183
backend: optix
source_limits: 16,64,128
frontier_row_capacity: 789009
grid_shape: 32,32,32
frontier_row_order: native
frontier_inline_nearest: true
```

Top-level result:

```text
all_matched: true
max_frontier_row_count: 528
median_route_wall_sec: 0.6765436306595802
```

Per case:

```text
source_limit=16:
  matched=true
  route_abs_diff=0.0
  frontier_rows=69
  capacity=789009
  policy=explicit
  native_symbol=rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
  frontier_row_order=native_unsorted
  inline_nearest=true
  total_candidate_distance_evaluations=11716

source_limit=64:
  matched=true
  route_abs_diff=0.0
  frontier_rows=294
  capacity=789009
  policy=explicit
  native_symbol=rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
  frontier_row_order=native_unsorted
  inline_nearest=true
  total_candidate_distance_evaluations=48825

source_limit=128:
  matched=true
  route_abs_diff=0.0
  frontier_rows=528
  capacity=789009
  policy=explicit
  native_symbol=rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
  frontier_row_order=native_unsorted
  inline_nearest=true
  total_candidate_distance_evaluations=91941
```

The row count is much smaller than Goal5181's local NumPy readiness artifact
because the native OptiX route uses `inline_nearest=true`: inline cell rows are
reduced inside the native frontier producer, leaving only offload rows for the
downstream continuation. That is expected and is not a new all-source claim.

## Code/Runner Fixes Needed For POD

Goal5183 also fixed a cross-platform paper-app path issue:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
```

The Goal5178 bridge artifact stores paths from Windows. On Linux/POD those
backslashes were interpreted literally. `_resolve_bridge_paths` now normalizes
backslashes to `/`, allowing the same artifact to be consumed by both Windows
and Linux runners.

The Goal5181/5182 scaling runner was also extended to include the native
frontier symbol, row order, and inline-nearest metadata in each compact
per-case route summary.

## Validation

Local focused validation after the changes:

```text
py -m unittest \
  tests.goal5182_xhd_explicit_frontier_capacity_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5180_xhd_full_public_feasibility_gate_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Observed:

```text
Ran 10 tests in 8.249s
OK
```

JSON validation:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_explicit_capacity_optix_goal5183_graphics_dragon_happy_buddha_2026-07-08.json
```

Both passed.

## Interpretation

Goal5183 validates the next safety gate after Goal5181/5182:

- explicit capacity is accepted by the native OptiX path;
- the native path does not overflow with `row_capacity=789009`;
- all bounded source limits match exact subset oracles;
- native symbol and capacity policy are recorded in the artifact.

This is stronger than Goal5182 because it exercises the actual POD/OptiX
backend. It still remains a bounded subset gate: only 16/64/128 Dragon source
points are used against the full HappyBuddha target.

## Next Step

Goal5184 should increase the source subset on POD/OptiX, for example:

```text
source_limits: 256,512,1024
backend: optix
frontier_row_capacity: 789009 or reviewed successor
```

The next gate should keep exact subset oracle validation while feasible. If
exact oracle cost becomes too high, the goal must explicitly switch validation
mode and explain the lost evidence. No all-source or performance-ratio claim is
authorized until a corresponding all-source route and fair denominator exist.
