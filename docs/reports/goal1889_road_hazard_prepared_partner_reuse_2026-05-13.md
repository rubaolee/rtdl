# Goal1889 - Road Hazard Prepared Partner Reuse Timing Row

Status: local-smoke-pass-pod-pending

Date: 2026-05-13

## Scope

Goal1889 extends the Goal1869 road-hazard timing harness with the Goal1886
prepared partner-device reuse path:

`road_hazard_priority_flags_optix_prepared_partner_device_columns(...)`

The comparison remains same-contract priority-flag output for the synthetic
road-hazard workload:

- v1.8 one-shot native OptiX road-hazard rows;
- v1.8 prepared native OptiX segment/polygon hit-count rows;
- Goal1869 v2.0 unprepared partner-owned priority columns;
- Goal1889 v2.0 prepared partner-owned priority columns with reusable triangle
  scene and reusable witness output columns.

The native engine remains generic; road/hazard meaning is owned by Python and
the partner tensor layer.

## Implementation

The existing `scripts/goal1869_road_hazard_v2_partner_perf.py` runner now
records `goal1889_prepared_reuse` under each partner result. The row measures
only repeated query time after:

- `prepare_segment_polygon_anyhit_optix_partner_device_scene(...)`;
- `allocate_segment_polygon_witness_partner_device_output_columns(...)`.

It also records ratios against the v1.8 one-shot row, the v1.8 prepared native
row, and the Goal1869 unprepared partner row.

## Pod Commands

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 512 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json
```

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 2048 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json
```

## Expected Evidence

Artifacts to collect:

- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`

Each artifact must include strict priority-flag parity, the dual v1.8 baselines,
the Goal1869 unprepared partner row, and the nested Goal1889 prepared reuse row.

## Local Linux Smoke

The RTX pod was unavailable, so Codex used the standing local Linux development
host for smoke validation only:

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`
- Disposable checkout: `/tmp/rtdl_goal1889_smoke`
- OptiX library: built locally with `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- Partner packages: isolated `PYTHONPATH=/tmp/rtdl_v2_partner_pydeps`

Artifacts:

- `docs/reports/goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_64.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_256.json`

These artifacts prove Linux/CUDA/OptiX/Torch/CuPy functional portability for the
new prepared row. They do not replace RTX 3090 pod timing evidence.

| Count | Partner | Goal1869 unprepared partner median (s) | Goal1889 prepared reuse median (s) | Prepared/unprepared ratio | Prepared/v1.8 prepared ratio |
| ---: | --- | ---: | ---: | ---: | ---: |
| 64 | CuPy | 0.0021360031 | 0.0012973080 | 0.607x | 5.962x |
| 64 | Torch | 0.0016321751 | 0.0008198121 | 0.502x | 3.767x |
| 256 | CuPy | 0.0022091491 | 0.0013275420 | 0.601x | 2.460x |
| 256 | Torch | 0.0017113100 | 0.0008016210 | 0.468x | 1.485x |

## Boundary

This goal can authorize only a narrow same-contract road-hazard prepared
partner-device timing row after pod evidence exists.

It does not authorize v2.0 release wording, whole-app speedup wording, broad RT-core speedup wording, package-install wording, or arbitrary PyTorch/CuPy acceleration claims.
