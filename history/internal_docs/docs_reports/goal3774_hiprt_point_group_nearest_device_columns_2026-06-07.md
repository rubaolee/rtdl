# Goal3774 HIPRT Point-Group Nearest Device Columns

## Purpose

Goal3774 adds the remaining generic HIPRT device-column output contract for the
Hausdorff/X-HD v2.10 parity lane:

- `rtdl_hiprt_write_prepared_point_group_nearest_witness_2d_device_columns`

The native contract remains app-agnostic. It writes one nearest-witness record
per query into caller-owned CUDA/Orochi output columns:

- `query_id`
- `neighbor_id`
- `distance`

This is a point/group nearest-witness typed stream, not a Hausdorff-specific
native endpoint.

## Design

Goal3773 already prepared HIPRT point-group bounds, traversed them through a
generic nearest-witness kernel, and reduced the maximum nearest distance on
device. Goal3774 adds a split-columns kernel over the same generic row buffer
and exposes it through Python as:

```python
prepared.write_device_nearest_witness_columns(
    query_points,
    radius=...,
    query_ids_out=...,
    neighbor_ids_out=...,
    distances_out=...,
)
```

The Python runtime validates that each output is a one-dimensional contiguous
CUDA partner column with the expected dtype and device:

- `query_ids_out`: `uint32`
- `neighbor_ids_out`: `uint32`
- `distances_out`: `float64`

HIPRT also now reuses an already-current Orochi/CUDA context when one exists,
and destroys only contexts that it owns. That is required for partner-owned
CUDA output columns, because arrays created by a partner such as CuPy live in
the active CUDA context.

## v2.10 Parity Effect

The v2.10 AMD/HIPRT parity matrix now records:

- `hausdorff_xhd` required feature added:
  `point_group_nearest_witness_output_columns_2d`
- `hausdorff_xhd` missing generic contracts: empty
- `hausdorff_xhd` parity stage: `ready_for_amd_functional_pod`

The matrix now has six apps ready for AMD functional pod validation, two apps
still needing generic HIPRT extensions, and two compatibility-only apps.

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3774_hiprt_point_group_nearest_device_columns_test tests.goal3773_hiprt_point_group_nearest_witness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Expected pod validation builds HIPRT and runs the same focused suite. On an
NVIDIA pod, this is CUDA/Orochi HIPRT functional evidence only. It is not AMD
hardware evidence. In short: not AMD hardware evidence.

## Claim Boundary

This goal does not authorize AMD performance claims, HIPRT release claims,
public speedup wording, broad RT-core wording, paper-reproduction wording,
whole-app acceleration wording, or true end-to-end zero-copy wording.

The output columns are partner-owned device-column buffers, but query inputs are still
host-packed for this narrow HIPRT path. AMD hardware validation remains pending.
