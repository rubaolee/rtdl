# Goal5146 - Native 3-D AABB Point-Membership Row Producer

## Verdict

`native_3d_aabb_point_membership_pod_gate_matched`

## Why This Goal Exists

Goal5145 added the dimension-generic NumPy oracle for Goal5140 cell-MBR
frontier row tables. That oracle is enough to specify 3-D behavior, but it is
not a native backend.

Goal5146 deliberately implements the next smaller system brick:

```text
3-D AABB index + 3-D query points
-> native OptiX broadphase point-membership rows
-> {query_id, indexed_id}
```

This is an app-neutral native 3-D broadphase producer. It is not the complete
cell-MBR nearest-state frontier backend.

## Native API Added

The native public C ABI now declares:

```text
rtdl_optix_prepare_aabb_index_3d
rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows
rtdl_optix_destroy_prepared_aabb_index_3d
```

The Python wrapper exposes:

```text
prepare_optix_aabb_index_3d(...)
collect_aabb_point_membership_pair_rows_3d_optix(...)
```

Input AABB records are app-neutral:

```text
{id, min_x, min_y, min_z, max_x, max_y, max_z}
```

Output rows are app-neutral:

```text
{query_id, indexed_id}
```

## Implementation Notes

- The OptiX workload uses a generic 3-D AABB custom-primitive index.
- The raygen launches one query per 3-D point.
- The any-hit path appends pair rows for every containing box.
- Rows are sorted and deduplicated before return, matching the existing 2-D
  AABB membership pattern.
- Overflow remains fail-closed through the `valid_count`/capacity contract.
- The generic implementation window contains no X-HD / Hausdorff / paper /
  `hd_exec` identity.

## Local Tests

Command:

```text
py -m unittest tests.goal5146_optix_aabb_index_3d_point_membership_test tests.goal5145_dimension_generic_cell_mbr_frontdoor_test tests.goal5144_cell_mbr_backend_assisted_gate_runner_test tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test tests.goal5140_generic_cell_mbr_traversal_abi_test
```

Result:

```text
Ran 17 tests OK
```

The local tests check:

- native symbols are declared and named generically;
- Python wrappers are exported;
- `pack_aabbs_3d` preserves 3-D fields and rejects reversed bounds;
- the synthetic gate fixture has discriminating expected rows.

## POD Evidence

POD preflight used the current wrapper and key:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Result:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

The current native OptiX library was built on POD with:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc
```

The POD gate result is:

```text
Paper-reproduction-apps/x-hd-paper/results/aabb_index_3d_point_membership_gate_pod.json
```

Key fields:

```text
backend = optix
contract = generic_aabb_point_membership_pair_rows_3d
native_generic_symbol = rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows
matched = true
valid_count = 5
expected_rows = [[100,10],[101,10],[101,11],[102,11],[103,12]]
observed_rows = [[100,10],[101,10],[101,11],[102,11],[103,12]]
```

## What This Proves

This proves that RTDL now has a native OptiX 3-D AABB point-membership row
producer and that it matches a discriminating synthetic fixture on real CUDA /
OptiX hardware.

It also proves that the POD access issue from earlier runs was operational
rather than fundamental: using `scripts/current_pod_ssh.py` and the current
identity works.

## What This Does Not Prove

This does not implement or claim:

- the complete Goal5140 native cell-MBR nearest-frontier backend;
- nearest-state payload pruning inside traversal;
- inline/offload/pruned frontier row production in native code;
- X-HD RT-core algorithm reproduction;
- X-HD performance improvement;
- exact paper dataset reproduction;
- full X-HD paper reproduction.

## Next System Step

The next native backend step should use this 3-D AABB row producer as a
broadphase brick and compare against the Goal5145 dimension-generic oracle:

```text
native 3-D AABB point-membership rows
-> generic nearest-state/frontier lowering
-> Goal5140 row table
```

Only after that can a true native Goal5140 cell-MBR backend claim be reviewed.
