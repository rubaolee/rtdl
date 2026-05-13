# Goal1889 - Road Hazard Prepared Partner Reuse Timing Row

Status: implementation-ready-for-pod

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

## Boundary

This goal can authorize only a narrow same-contract road-hazard prepared
partner-device timing row after pod evidence exists.

It does not authorize v2.0 release wording, whole-app speedup wording, broad RT-core speedup wording, package-install wording, or arbitrary PyTorch/CuPy acceleration claims.
