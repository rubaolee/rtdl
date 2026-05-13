# Goal1868 - Road Hazard Partner Priority Flags Pod Smoke Plan

Status: ready-for-pod

Date: 2026-05-13

## Scope

Goal1868 adds a progress-printing pod-smoke runner for the Goal1865
`road_hazard_screening` partner priority-flag adapter:

`scripts/goal1868_road_hazard_partner_priority_flags_pod_smoke.py`

The runner builds caller-owned Torch/CuPy CUDA columns, invokes:

`rtdsl.road_hazard_priority_flags_optix_partner_device_columns(...)`

and validates partner-owned:

- `road_ids`
- `hit_counts`
- `priority_flags`

against deterministic expected counts and threshold flags.

## Intended Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal1868_road_hazard_partner_priority_flags_pod_smoke.py \
  --count 16 \
  --threshold 2 \
  --partners cupy,torch \
  --output docs/reports/goal1868_road_hazard_partner_priority_flags_pod_smoke.json
```

The runner prints `[setup]`, `[partner]`, and `[artifact]` progress markers so a
long pod run is not silent.

## Boundary

This plan does not contain hardware evidence yet. It does not authorize v2.0
release wording, whole-application speedup wording, broad RT-core speedup
wording, or an all-app v2.0-vs-v1.8 performance table.
