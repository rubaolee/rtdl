# V4 Point-Group Device-Array Front Door

Status: measured V4 surface; final release authorization pending

This page documents the point-group nearest-witness measured surface:

- `v4_point_group_nearest_witness_2d_device_arrays`

The surface is generic: it finds the nearest witness point for each query point
within prepared point groups. It is not a Hausdorff, collision, or app-specific
kernel.

## API Shape

Use the V4 module surface directly:

```python
import rtdsl.v4_point_group as pg_v4

with pg_v4.prepare_point_group_nearest_witness_2d_device_arrays_v4(
    search_points,
    point_groups,
    max_radius=0.5,
    partner="torch",
) as session:
    output_columns = session.allocate_outputs(query_point_columns)
    result = session.run(
        query_point_columns,
        radius=0.5,
        output_columns=output_columns,
        return_metadata=True,
    )
```

Current input contract:

- `search_points`: prepared by RTDL into a native point-group scene
- `point_groups`: prepared by RTDL into native group bounds
- `query_point_columns`: caller-owned Torch CUDA columns `ids`, `x`, `y`

Output columns:

- `query_ids`: `torch.uint32`, CUDA
- `neighbor_ids`: `torch.uint32`, CUDA
- `distances`: `torch.float64`, CUDA. Values are computed at float32
  precision by the native path and written into the float64 column.

## Minimal Example

Run on a CUDA/OptiX machine:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/path/to/librtdl_optix.so
python examples/v4/point_group_nearest_witness_torch_device_arrays.py --query-count 8192
```

Dry-run locally without CUDA:

```bash
python examples/v4/point_group_nearest_witness_torch_device_arrays.py --dry-run
```

## Evidence

RTX A5000 POD repeat-gate evidence:

| queries | direct device-output median | legacy host-row median | same-contract ratio | parity |
|---:|---:|---:|---:|---|
| 32,768 | 0.000529s | 0.351068s | 663.143x | true |
| 131,072 | 0.000507s | 0.947073s | 1868.088x | true |

The repeat gate uses a non-trivial correctness fixture with equal counts of
exact matches, positive-offset nonzero distances, no-hit rows, and
negative-offset nonzero distances. No-hit rows use neighbor id `0xFFFFFFFF` and
float32 max distance.

RTX A5000 POD smoke evidence also passed at 8,192 query points.

Additional `mixed6` RTX A5000 POD evidence covers diagonal hit and diagonal
no-hit rows:

| queries | direct device-output median | legacy host-row median | same-contract ratio | parity |
|---:|---:|---:|---:|---|
| 32,768 | 0.000575s | 0.292999s | 509.391x | true |
| 131,072 | 0.000476s | 0.886679s | 1863.097x | true |

Source evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.md`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`
- `future/v4/evidence/v4_goal4618_point_group_mixed6_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_goal4618_point_group_mixed6_pod_gate_32768_131072_2026-06-24.json`

The goal4618 promotion decision moved this surface into the measured catalog
with Torch CUDA / OptiX 8.0 / RTX A5000 scope. CuPy and OptiX 9.1 remain
unmeasured.

## Important Boundary

This surface does not carry a public true-zero-copy claim. Query and output
columns are caller-owned Torch CUDA arrays in the hot run, but the prepared
search points and group bounds are RTDL-owned native data.

## Non-Claims

This page does not authorize:

- final V4 release before Goal4642
- broad V4 speedup wording
- whole-application speedup wording
- true-zero-copy public wording
- Tier-3 callback/PTX claims
- raw OptiX callback support
- app-specific native engine claims
