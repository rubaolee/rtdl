# V4 Primitive Grouped-I64 Device Outputs Local Gate

Date: 2026-06-24
Status: local Linux candidate gate passed; not release or public performance evidence

## Surface

`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

This is a V4 Tier-2 candidate promoted from the V2/V2.x generic
`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` primitive. It is not yet a
measured V4.0 release surface.

## Environment

- Host: `lx1`
- GPU: NVIDIA GeForce GTX 1070
- Python: 3.12.3
- Torch: 2.12.1+cu126
- Native backend: rebuilt with `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev CUDA_PREFIX=/usr`

Because this is a GTX 1070 local machine, these timings do not authorize any
RT-core POD performance wording.

## Gate

Command:

```bash
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
PYTHONPATH=src:. \
python3 scripts/v4_primitive_grouped_i64_device_outputs_validation.py \
  --ray-counts 8192,32768 \
  --group-width 16 \
  --repeat 5 \
  --warmup 2 \
  --json-out future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_8192_32768_2026-06-24.json
```

## Result

| Rays / triangles | Groups | Parity | Device-output median (s) | Legacy host-output median (s) | Local ratio |
| --- | ---: | --- | ---: | ---: | ---: |
| 8,192 | 512 | pass for `sum_count`, `min`, `max` | 0.000130703 | 0.000357760 | 2.737x |
| 32,768 | 2,048 | pass for `sum_count`, `min`, `max` | 0.000196054 | 0.001056885 | 5.391x |

The ratio is `legacy_host_output / direct_device_output` on the local GTX gate.
It measures removal of grouped-row host materialization for this candidate
front door. It is not a broad V4 speedup claim.

## What This Proves

- The new native symbol is exported by `build/librtdl_optix.so`.
- The V4 Python front door can run end-to-end on Torch CUDA device columns.
- Direct device-output columns match both the legacy host-output primitive and
  the analytic fixture for `sum_count`, `min`, and `max`.
- Metadata reports `native_direct_device_output_columns: true` and
  `group_rows_downloaded_to_host_in_hot_path: false`.

## What Remains

- Same-contract POD validation on RT hardware before moving this candidate into
  the measured V4 catalog.
- Comparison against the older hit-stream + partner continuation route where
  feasible.
- External review before any release-surface promotion.

## Pod Runner Smoke

The reusable runner `scripts/v4_primitive_grouped_i64_pod_gate.sh` was smoke
tested on `lx1` with `RAY_COUNTS=8192 REPEAT=2 WARMUP=1`. It rebuilt the native
OptiX backend, ran the same validation gate, and wrote:

- `future/v4/evidence/v4_primitive_grouped_i64_pod_gate_runner_lx1_smoke_2026-06-24.json`
