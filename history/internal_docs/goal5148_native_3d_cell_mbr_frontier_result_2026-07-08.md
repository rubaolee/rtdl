# Goal5148 Native 3D Cell-MBR Frontier Result

## Verdict

`completed_bounded_native_3d_cell_mbr_frontier_pod_matched`

Goal5148 implements and validates a bounded, app-neutral native OptiX 3-D
cell-MBR nearest-frontier row producer. It moves the Goal5147 path's exact
point-to-cell-MBR distance filter and nearest-state frontier kind classification
from Python/NumPy into native OptiX traversal for 3-D.

This is still not a full 2-D/3-D Goal5140 native ABI backend and is not an X-HD
paper-performance claim.

## What Changed

### Native OptiX

Added the C ABI symbol:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d
```

The symbol accepts generic query coordinates, query point ids, cell ids, cell
MBR min/max bounds, cell point-span descriptors, current nearest-state
distances, and `max_inline_points`. It emits the Goal5140 row-table columns:

```text
frontier_kind_codes
query_row_ids
query_point_ids
cell_ids
point_begin_offsets
point_counts
min_distances
max_distances
```

The native pipeline uses OptiX custom AABB traversal over expanded cell MBRs.
Inside the custom intersection/any-hit path it computes exact point-to-cell-MBR
minimum and maximum distances, applies the radius filter, and classifies rows as
inline/offload/pruned:

```text
1 = inline
2 = offload
3 = pruned
```

Overflow is fail-closed: if attempted rows exceed capacity, the native ABI
reports overflow and emits no usable partial row table.

### Python/RTDL Surface

Added:

```text
collect_cell_mbr_nearest_frontier_3d_optix
cell_mbr_nearest_frontier_native_3d_optix_columns
```

and updated:

```text
plan_cell_mbr_traversal_lowering("optix_3d")
```

The public wrapper returns the same generic Goal5140 row-table schema used by
the NumPy oracle and by Goal5147's backend-assisted route.

## Validation

### Local

```text
py -m unittest \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5147_backend_assisted_3d_cell_mbr_frontdoor_test \
  tests.goal5146_optix_aabb_index_3d_point_membership_test \
  tests.goal5140_generic_cell_mbr_traversal_abi_test

Ran 15 tests in 0.810s
OK
```

The local tests verify:

- native symbol declarations exist;
- the native/source window is app-neutral;
- the public lowering plan exposes a bounded native 3-D OptiX target;
- the Python wrapper wires generic query/cell arrays to the native row-table
  contract;
- no X-HD or paper-specific semantic leaks appear in the generic API window.

### POD

POD preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

OptiX backend build:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc
exit code: 0
```

POD gate:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_native_3d_cell_mbr_frontier_gate.py \
  --output Paper-reproduction-apps/x-hd-paper/results/native_3d_cell_mbr_frontier_gate_pod_optix.json
```

Result:

```text
matched = true
schema = rtdl.paper_reproduction.xhd.native_3d_cell_mbr_frontier_gate.v1
status = native_3d_cell_mbr_frontier_gate_completed
native_generic_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
row_count = 6
frontier_kind_codes = [1,1,1,2,3,3]
mismatched_columns = []
```

The native columns exactly matched the Goal5145 dimension-generic oracle on the
synthetic 3-D fixture.

POD focused test:

```text
python3 -m unittest tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 3 tests in 0.309s
OK
```

## Claim Boundary

Authorized:

- bounded app-neutral native OptiX 3-D cell-MBR frontier row producer;
- exact point-to-cell-MBR radius filtering inside native traversal;
- nearest-state frontier kind classification inside native traversal;
- matching Goal5145 oracle on the bounded 3-D fixture.

Not authorized:

- full 2-D/3-D Goal5140 native ABI backend complete;
- X-HD paper performance reproduction;
- whole-program speedup;
- exact paper dataset reproduction;
- author-performance parity;
- application-specific X-HD primitive in RTDL core.

## Remaining Work

The next hard steps are:

1. Decide whether to extend this bounded 3-D symbol into the full
   `rtdl_optix_collect_cell_mbr_nearest_frontier` 2-D/3-D ABI or keep the
   bounded 3-D symbol as a stepping stone.
2. Connect the native 3-D row-table route to a representative X-HD-style sample
   route and compare against the current exact columnar/reference route.
3. Only after representative integration, measure performance under honest
   regime and phase boundaries.
