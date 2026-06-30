# Goal989 Service-Coverage Scalar Threshold Profiler

Date: 2026-04-26

Goal989 changes the service-coverage OptiX phase profiler to use scalar prepared threshold count instead of materializing one count row per household. It does not authorize public RTX speedup claims.

## Motivation

Goal978 classified `service_coverage_gaps / prepared_gap_summary` as internal-only because RTX was only marginally faster than the fastest same-semantics non-OptiX baseline. The current path should remove avoidable row-output cost before the next RTX artifact.

The cloud profiler's compact service-coverage result only needs covered and uncovered household counts. It does not need uncovered household identities.

## Change

`scripts/goal811_spatial_optix_summary_phase_profiler.py` now uses:

```text
prepared.count_threshold_reached(households, radius=RADIUS, threshold=1)
```

for the `service_coverage_gaps` OptiX phase path.

The profiler now returns:

- `covered_household_count`,
- `uncovered_household_count`,
- `summary_mode: scalar_threshold_count`,
- and `uncovered_household_ids: None` to make clear that this compact benchmark path does not emit household identities.

## Boundary

This is a compact-summary profiler optimization. It does not change the row-returning app path, and it does not claim full service-coverage optimization or nearest-clinic assignment acceleration.

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
Ran 30 tests in 0.131s
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
  --scenario service_coverage_gaps \
  --mode optix \
  --copies 20000 \
  --output-json docs/reports/goal811_service_coverage_rtx.json
```

The expected result is lower query/postprocess overhead for the compact coverage-count benchmark path.
