# Goal1848 OptiX Partner Bounded All-Witness Output Contract

Date: 2026-05-13
Status: `pass-with-boundary`

## Purpose

Goal1848 extends the Goal1845/Goal1847 first-hit witness path into the bounded
all-hit witness contract needed by app-level row adapters. The new contract keeps
the RTDL engine generic: it writes ray/primitive witness pairs, not
segment/polygon rows or app-specific records.

## Change

Added a narrow OptiX prepared any-hit ABI:

```text
rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses
```

The ABI reads partner-owned CUDA ray columns and a triangle-column zero-copy
prepared scene, then writes bounded partner-owned CUDA `uint32` output columns:

- `witness_ray_ids`
- `witness_primitive_ids`

It also returns host-side `emitted_count` and `overflowed` counters. Exact row
semantics are authorized only when `overflowed == false`.

Python exposes this through:

```python
rt.pack_optix_ray_any_hit_2d_device_all_witness_outputs(...)
scene.write_device_any_hit_all_witnesses(...)
```

The validator requires both output columns to be one-dimensional contiguous
`uint32` buffers on the same CUDA device as the partner-owned ray columns. The
two output columns must have matching shape; their length is the witness
capacity.

## Boundary

This is a bounded all-hit witness contract, not an application row contract. It
is sufficient for an app-level adapter to reconstruct
`segment_polygon_anyhit_rows` style pairs if the adapter owns the ray-to-app-row
mapping and the run does not overflow. The native engine still only emits
generic ray and primitive IDs.

This goal does not authorize broad RT-core speedup, whole-application
acceleration, arbitrary PyTorch/CuPy acceleration, package installation, or
v2.0 release readiness. The hardware pod validation below counts only as
execution evidence for this bounded all-witness output contract.

## Pod Validation

The contract was built and validated on an NVIDIA RTX A4500 pod:

```text
GPU: NVIDIA RTX A4500
Driver: 550.127.05
Python: 3.11.10
Torch: 2.4.1+cu124
CuPy: 14.0.1
OptiX SDK: /root/vendor/optix-sdk
CUDA: /usr/local/cuda
```

Commands:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=/root/rtdl/build:${LD_LIBRARY_PATH:-}

python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner cupy \
  --goal Goal1848-CuPy \
  --output-all-witnesses \
  --output docs/reports/goal1848_optix_partner_all_witness_cupy_pod_validation.json

python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner torch \
  --goal Goal1848-Torch \
  --output-all-witnesses \
  --output docs/reports/goal1848_optix_partner_all_witness_torch_pod_validation.json
```

Expected bounded witness checks:

```text
observed_all_witness_pairs_sorted == [(101, 11), (101, 12)]
claim_boundary.bounded_all_hit_witness_identity_observed == true
output_metadata.overflowed == false
```

Both partner runs passed:

```text
CuPy status: pass
Torch status: pass
```

This is not a v2.0 release gate pass.
