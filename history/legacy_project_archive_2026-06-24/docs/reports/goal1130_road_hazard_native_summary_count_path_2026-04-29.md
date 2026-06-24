# Goal1130 Road-Hazard Native Summary Count Path

Date: 2026-04-29

## Scope

Goal1130 narrows `examples/rtdl_road_hazard_screening.py` so the native OptiX
`summary` path can use the prepared segment/polygon threshold-count API instead
of materializing per-road hit-count rows and then counting hot roads in Python.

This is a code-path readiness change, not a public RTX speedup promotion.
`road_hazard_screening` remains gated by strict segment/polygon RTX evidence and
public wording review.

## Implementation

- `--backend optix --optix-mode native --output-mode summary` now calls
  `rt.prepare_optix_segment_polygon_hitcount_2d(...).count_at_least(...,
  threshold=2)`.
- The native summary path does not call `rt.run_optix`, does not call
  `prepared.run`, and does not materialize priority segment ids.
- `--output-mode priority_segments` still materializes hit-count rows because
  that public mode returns segment ids.
- The payload records phase timings:
  `input_construction_sec`, `native_prepare_sec`,
  `native_threshold_count_sec`, and `native_close_sec` for the native summary
  path.
- `rt_core_accelerated` remains `false` and `--require-rt-core` remains blocked
  until strict real-RTX artifacts and review promote the path.

## Local Evidence

Local macOS has no OptiX runtime, so this goal uses contract tests for the
native prepared API and local CPU/Embree probes for same app semantics.

| Artifact | Backend | Rows | Priority count | Materializes rows |
|---|---:|---:|---:|---:|
| `docs/reports/goal1130_road_hazard_local_cpu_summary_2026-04-29.json` | `cpu_python_reference` | 3000 | 1000 | true |
| `docs/reports/goal1130_road_hazard_local_embree_summary_2026-04-29.json` | `embree` | 3000 | 1000 | true |

The real native OptiX summary path is cloud-ready but still needs an RTX pod
artifact before any public acceleration wording changes.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1130_road_hazard_native_summary_count_test \
  tests.goal888_road_hazard_native_optix_gate_test \
  tests.goal933_prepared_segment_polygon_profiler_test \
  tests.goal956_segment_polygon_native_continuation_metadata_test \
  tests.goal820_segment_polygon_rt_core_gate_test -v

Ran 24 tests in 0.276s
OK
```

## Claim Boundary

Accepted wording for this goal is only:

> Road-hazard native OptiX summary has a count-only prepared API path in code
> and is ready for real RTX artifact collection.

Forbidden wording:

- Do not claim road-hazard is publicly RTX accelerated.
- Do not claim whole-app road-hazard speedup.
- Do not claim GIS routing, risk scoring, or row-returning road-hazard outputs
  are accelerated by this change.
- Do not claim priority segment id output avoids row materialization.
