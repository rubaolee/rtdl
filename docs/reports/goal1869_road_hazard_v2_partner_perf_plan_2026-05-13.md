# Goal1869 - Road Hazard v2 Partner Performance Plan

Status: ready-for-pod

Date: 2026-05-13

## Scope

Goal1869 adds a pod-ready timing harness for the Goal1865 road-hazard partner
priority-flag adapter:

`scripts/goal1869_road_hazard_v2_partner_perf.py`

The measured app is `road_hazard_screening`. The comparison is:

- v1.8/current one-shot native OptiX road-hazard hit-count rows:
  `rt.run_optix(road_hazard_hitcount, ...)`
- v1.8/current prepared native OptiX segment/polygon hit-count rows:
  `prepare_optix_segment_polygon_hitcount_2d(...).run(...)`
- v2.0 preview caller-supplied partner-column path:
  `road_hazard_priority_flags_optix_partner_device_columns(...)`

The parity contract is per-road priority flags produced from the same
hit-count threshold.

## Intended Pod Commands

```bash
PYTHONPATH=src:. python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 512 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1869_road_hazard_v2_partner_perf_pod_512.json
```

```bash
PYTHONPATH=src:. python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 2048 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1869_road_hazard_v2_partner_perf_pod_2048.json
```

The runner prints `[setup]`, `[timing]`, and `[artifact]` progress markers for
pod use.

## Boundary

This is a plan and local harness only. It does not contain pod timing evidence
yet and does not authorize v2.0 release wording, whole-application speedup
wording, broad RT-core speedup wording, or an all-app v2.0-vs-v1.8 performance
table.
