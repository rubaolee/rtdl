# Goal3034 - Point-Group Nearest Device Columns L4 Pod Validation

Date: 2026-06-02

## Purpose

Goal3033 added a generic OptiX producer for prepared point-group nearest-witness rows:

`rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns`

This validation records that the new native ABI builds and runs from a clean
source checkout on the L4 pod, and that the device output columns match the
existing raw row-view contract.

## Environment

- Pod: `root@157.157.221.29 -p 29842`
- GPU: NVIDIA L4, driver 565.57.01
- CUDA: `/usr/local/cuda-12.6`
- OptiX SDK: `/root/vendor/optix-sdk`
- Source commit: `a4f867d833edea0b30e4a8e7650243bb371eb60e`
- Source dirty state: `[]`

The pod checkout was reset to `origin/main`, rebuilt with:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.6
```

## Validation

The focused unit tests passed on the pod:

```text
Ran 8 tests in 0.412s

OK
```

The runtime probe prepared 3,072 target points in 16 groups, launched the
generic RT-core nearest-witness path for 2,048 query points, and wrote three
caller-owned CuPy output columns:

- `query_ids:uint32`
- `neighbor_ids:uint32`
- `distances:float64`

Those device columns were copied back only for validation and compared against
the existing `nearest_witness_raw(...).to_numpy(copy=True)` row-view result:

| Check | Result |
| --- | --- |
| Query ids match raw rows | true |
| Neighbor ids match raw rows | true |
| Distances match raw rows | true |
| Materializes host neighbor rows on the new path | false |
| RT-core accelerated native path | true |
| Native elapsed time in this small correctness probe | 0.3129175677895546 s |

## Claim Boundary

This validates a new internal generic producer contract, not a release claim.
It does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- package-install claims
- app-specific native-engine behavior

The output columns are caller-owned CUDA device buffers, so the producer avoids
host row materialization on its output side. The call still uploads host query
points for this first slice, and the report therefore keeps
`true_zero_copy_authorized=false`.

## Next Work

The next useful step is a device-resident consumer over these columns: for
Hausdorff-style workloads, that means a generic grouped/global max-distance
witness reducer that consumes `query_ids`, `neighbor_ids`, and `distances`
without copying a row table back to the host. That would turn this producer
from a correctness primitive into a real end-to-end continuation path.
