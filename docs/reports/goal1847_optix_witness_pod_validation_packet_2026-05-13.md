# Goal1847 OptiX Witness Pod Validation Packet

Date: 2026-05-13
Status: `pass-with-boundary`

## Purpose

Goal1847 records the hardware validation run for Goal1845's first-hit witness
output contract. The run was executed on an NVIDIA RTX A4500 pod against commit
`761d8daa`, after building `librtdl_optix.so` from source.

The pod run validates that both PyTorch and CuPy can hand GPU-resident ray
columns, triangle columns, AABB columns, and witness output buffers directly to
the OptiX native layer through the partner tensor protocol. It validates a
first-hit witness identity contract only; it does not validate full multi-hit
row collection.

## Commands

The pod was synced to commit `761d8daa` and used:

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
  --goal Goal1847-CuPy \
  --output-witnesses \
  --output docs/reports/goal1847_optix_partner_witness_cupy_pod_validation.json

python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner torch \
  --goal Goal1847-Torch \
  --output-witnesses \
  --output docs/reports/goal1847_optix_partner_witness_torch_pod_validation.json
```

## Results

Both partner runs passed:

```text
CuPy status: pass
Torch status: pass
```

Observed witness checks:

```text
observed_witness_ray_ids == [101, 102]
observed_witness_primitive_ids == [11, 4294967295]
```

`4294967295` is the unsigned `0xFFFFFFFF` no-hit sentinel.

For both partners, the JSON artifacts record:

```text
claim_boundary.ray_column_true_zero_copy_observed == true
claim_boundary.triangle_scene_true_zero_copy_observed == true
claim_boundary.witness_outputs_true_zero_copy_observed == true
claim_boundary.first_hit_witness_identity_observed == true
claim_boundary.rt_core_speedup_claim_authorized == false
claim_boundary.v2_0_release_authorized == false
```

## Boundary

Passing this packet validates Goal1845 as hardware execution evidence for a
first-hit witness output contract. It does not validate the full multi-hit
`segment_polygon_anyhit_rows` row collector, broad RT-core speedup,
whole-application acceleration, arbitrary PyTorch/CuPy acceleration, package
installation, or v2.0 release readiness.

This is not a v2.0 release gate pass.
