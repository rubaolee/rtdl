# Goal1847 OptiX Witness Pod Validation Packet

Date: 2026-05-13
Status: `pod-required`

## Purpose

Goal1847 prepares the hardware validation command for Goal1845's first-hit
witness output contract. No hardware run is recorded in this packet.

## Commands

After syncing a pod to a commit that includes Goal1845/Goal1847 and building
OptiX:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner cupy \
  --goal Goal1847-CuPy \
  --output-witnesses \
  --output docs/reports/goal1847_optix_partner_witness_cupy_pod_validation.json
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner torch \
  --goal Goal1847-Torch \
  --output-witnesses \
  --output docs/reports/goal1847_optix_partner_witness_torch_pod_validation.json
```

Expected witness checks:

```text
observed_witness_ray_ids == [101, 102]
observed_witness_primitive_ids == [11, 4294967295]
```

`4294967295` is the unsigned `0xFFFFFFFF` no-hit sentinel.

## Boundary

Passing this packet would validate Goal1845 as hardware execution evidence for a
first-hit witness output contract. It would not validate the full multi-hit
`segment_polygon_anyhit_rows` row collector, broad RT-core speedup,
whole-application acceleration, arbitrary PyTorch/CuPy acceleration, package
installation, or v2.0 release readiness.

This is not a v2.0 release gate pass.
