# Goal5147 - Backend-Assisted 3-D Cell-MBR Front Door

## Verdict

`backend_assisted_3d_cell_mbr_frontdoor_matched_oracle`

## Why This Goal Exists

Goal5146 proved a native OptiX 3-D AABB point-membership row producer. By
itself, that only emits broadphase rows:

```text
{query_id, indexed_id}
```

X-HD's algorithmic route needs those broadphase rows to feed a cell-MBR
nearest-state/frontier pipeline. Goal5147 connects the native 3-D AABB
broadphase brick to the existing generic NumPy exact filter and frontier
lowering:

```text
native/CPU 3-D AABB membership rows
-> exact point-to-cell-MBR distance filter
-> nearest-state frontier split
-> Goal5140 ABI-shaped row table
```

This is still a backend-assisted front door, not a fully native traversal
backend.

## Public API Added

```text
cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns(...)
```

It is exported from `rtdsl.__all__`.

Supported broadphase backends:

```text
backend="cpu"
backend="optix"
```

Metadata contract:

```text
contract = generic_cell_mbr_nearest_frontier_aabb_membership_3d
native_abi_contract = generic_cell_mbr_nearest_frontier_native_abi_v1
native_engine_row_contract = backend_assisted_aabb_membership_plus_numpy_frontier_classification
native_backend_complete = false
app_semantics = none
```

`plan_cell_mbr_traversal_lowering("aabb_membership_3d")` now reports:

```text
status = implemented_backend_assisted_3d_frontdoor
executable = true
native_backend_complete = false
backend_options = ("cpu", "optix")
```

## Local CPU Evidence

Command:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_cell_mbr_backend_assisted_3d_gate.py --backend cpu --output Paper-reproduction-apps/x-hd-paper/results/backend_assisted_3d_cell_mbr_gate_cpu.json
```

Result:

```text
matched = true
backend = cpu
broadphase_contract = generic_expanded_aabb_point_membership_rows_3d_v1
row_count = 6
```

The assisted route matched the Goal5145 dimension-generic oracle exactly:

```text
query_point_ids     = [100, 101, 102, 102, 100, 101]
cell_ids            = [0, 0, 0, 1, 1, 1]
frontier_kind_codes = [1, 1, 1, 2, 3, 3]
```

## POD OptiX Evidence

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Result:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD gate:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_cell_mbr_backend_assisted_3d_gate.py --backend optix --output Paper-reproduction-apps/x-hd-paper/results/backend_assisted_3d_cell_mbr_gate_pod_optix.json
```

Result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/backend_assisted_3d_cell_mbr_gate_pod_optix.json
```

Key fields:

```text
matched = true
backend = optix
broadphase_contract = generic_aabb_point_membership_pair_rows_3d
broadphase_native_symbol = rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows
row_count = 6
```

## Tests

Command:

```text
py -m unittest tests.goal5147_backend_assisted_3d_cell_mbr_frontdoor_test tests.goal5146_optix_aabb_index_3d_point_membership_test tests.goal5145_dimension_generic_cell_mbr_frontdoor_test tests.goal5144_cell_mbr_backend_assisted_gate_runner_test tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test tests.goal5140_generic_cell_mbr_traversal_abi_test
```

Result:

```text
Ran 21 tests OK
```

The new tests verify:

- CPU backend-assisted 3-D route matches the Goal5145 oracle;
- expanded AABB corner false positives are removed by exact point-to-MBR
  distance filtering;
- output capacity overflow fails closed;
- the public function and lowering plan remain app-neutral and avoid X-HD /
  Hausdorff / paper / author vocabulary.

## What This Proves

RTDL now has a generic executable 3-D backend-assisted cell-MBR front door.
For the tested 3-D fixture:

- CPU broadphase rows match the oracle;
- native OptiX 3-D AABB broadphase rows match the same oracle;
- row-table output matches the Goal5140 ABI-shaped columns.

## What This Does Not Prove

This does not implement or claim:

- a fully native/fused Goal5140 cell-MBR nearest-frontier backend;
- in-traversal nearest-state payload pruning;
- native inline/offload/pruned frontier row production;
- X-HD RT-core algorithm reproduction;
- X-HD performance improvement;
- exact paper dataset reproduction;
- full X-HD paper reproduction.

The important remaining gap is that exact filtering and frontier classification
still run in generic NumPy after broadphase rows are materialized.

## Next System Step

The next backend step is to move more of the Goal5140 row-table production into
native traversal:

```text
native 3-D AABB broadphase
-> native point-to-cell-MBR distance filter
-> native nearest-state payload / prune decision
-> native row-table emission
```

Until that exists, the route remains backend-assisted rather than complete
native traversal.
