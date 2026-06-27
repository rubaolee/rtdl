# Goal1889 - Road Hazard Prepared Partner Reuse Timing Row

Status: pod-pass-with-boundary

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

## Goal2006 Pod Follow-Up

Goal2006 reran the prepared CuPy row on an RTX A5000 pod after the Goal2000 /
Goal2003 candidate-witness exact-filter correction. The reusable prepared scene
now retains the caller-owned triangle columns, allowing the CuPy RawKernel exact
segment/triangle filter to run before partner-side unique-pair counting.

Artifact:

- `docs/reports/goal2006_pod_smoke/road_hazard_prepared_cupy_exact_filter_2048.json`

Result at `count=2048`, `iterations=5`:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 16.327098407 | 4699.62x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.003474137 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.003750768 | 1.080x |
| Goal2006 prepared CuPy exact-filter priority columns | 0.003149398 | 0.907x |

Strict priority-flag parity passed. This upgrades the CuPy prepared road-hazard
row from pod-pending to measured-with-boundary, while keeping the v2.0 release
and broad-speedup claims blocked.

## Local Linux Smoke

The RTX pod was unavailable, so Codex used the standing local Linux development
host for smoke validation only:

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`
- Disposable checkout: `/tmp/rtdl_goal1889_smoke`
- OptiX library: built locally with `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- Partner packages: isolated `PYTHONPATH=/tmp/rtdl_v2_partner_pydeps`
- Source label recorded in artifacts: `a63c706b7a0488c161d6f8e090de5e441a710f7f`

Artifacts:

- `docs/reports/goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_64.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_256.json`

These artifacts prove Linux/CUDA/OptiX/Torch/CuPy functional portability for the
new prepared row. They do not replace RTX 3090 pod timing evidence.

| Count | Partner | Goal1869 unprepared partner median (s) | Goal1889 prepared reuse median (s) | Prepared/unprepared ratio | Prepared/v1.8 prepared ratio |
| ---: | --- | ---: | ---: | ---: | ---: |
| 64 | CuPy | 0.0021506679 | 0.0013114880 | 0.610x | 5.610x |
| 64 | Torch | 0.0016408029 | 0.0008181380 | 0.499x | 3.500x |
| 256 | CuPy | 0.0021917709 | 0.0012984910 | 0.592x | 2.464x |
| 256 | Torch | 0.0017182761 | 0.0008294451 | 0.483x | 1.574x |

## Boundary

This goal can authorize only a narrow same-contract road-hazard prepared
partner-device timing row after pod evidence exists.

It does not authorize v2.0 release wording, whole-app speedup wording, broad RT-core speedup wording, package-install wording, or arbitrary PyTorch/CuPy acceleration claims.
