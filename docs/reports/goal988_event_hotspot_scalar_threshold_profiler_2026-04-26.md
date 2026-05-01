# Goal988 Event-Hotspot Scalar Threshold Profiler

Date: 2026-04-26

Goal988 changes the event-hotspot OptiX phase profiler to use the existing prepared scalar threshold-count continuation instead of materializing one count row per event. It does not authorize public RTX speedup claims.

## Motivation

Goal978 rejected the current `event_hotspot_screening / prepared_count_summary` public speedup claim because the RTX path was slower than the fastest same-semantics non-OptiX baseline.

The cloud profiler's compact event-hotspot result only needs a hotspot count. It does not need each event id or a per-event neighbor-count row.

Because event rows are self-joins, the app's hotspot rule is:

```text
neighbor_count_without_self >= HOTSPOT_THRESHOLD
```

The prepared fixed-radius threshold-count primitive includes the query point itself, so the equivalent scalar threshold is:

```text
threshold = HOTSPOT_THRESHOLD + 1
```

## Change

`scripts/goal811_spatial_optix_summary_phase_profiler.py` now uses:

```text
prepared.count_threshold_reached(events, radius=RADIUS, threshold=HOTSPOT_THRESHOLD + 1)
```

for the `event_hotspot_screening` OptiX phase path.

The profiler now returns:

- `hotspot_count`,
- `summary_mode: scalar_threshold_count`,
- `threshold_includes_self`,
- and `hotspots: None` to make clear that this compact benchmark path does not emit hotspot identities.

## Boundary

This is a compact-summary profiler optimization. It does not change the row-returning app path, and it does not claim whole-app event analytics speedup.

This goal does not authorize public RTX speedup claims. A fresh RTX artifact must be compared against same-semantics baselines and independently reviewed before any public wording changes.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal811_spatial_optix_summary_phase_profiler_test \
  tests.goal826_tier2_phase_profiler_contract_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal705_optix_app_benchmark_readiness_test
```

Result:

```text
Ran 30 tests in 0.129s
OK
```

Additional checks:

```text
python3 -m py_compile scripts/goal811_spatial_optix_summary_phase_profiler.py
git diff --check
```

Both passed.

## Next Cloud Action

On the next RTX pod, rerun:

```text
python3 scripts/goal811_spatial_optix_summary_phase_profiler.py \
  --scenario event_hotspot_screening \
  --mode optix \
  --copies 20000 \
  --output-json docs/reports/goal811_event_hotspot_rtx.json
```

The expected result is lower query/postprocess overhead for the compact hotspot-count benchmark path. If it remains slower than Embree, the next target is larger-scale batching or device-side aggregate profiling rather than row-output optimization.
