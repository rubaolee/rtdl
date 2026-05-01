# Goal920: Facility Coverage RTX Readiness Promotion

Date: 2026-04-25

## Purpose

Promote only the bounded `facility_knn_assignment` service-coverage decision
sub-path after verifying that the existing Goal887 RTX artifact has a
same-scale local CPU oracle baseline. This does not promote ranked KNN
assignment.

## Local Fix

`facility_coverage_oracle(...)` was quadratic over customers and depots, which
made same-scale local validation impractical at `copies=20000`. Goal920
replaces it with an exact grid-neighborhood oracle:

- radius `0` uses exact coordinate matching;
- positive radii index depots by grid cell and check only neighboring cells;
- the final predicate remains exact squared-distance comparison.

This is an oracle/performance cleanup for validation and does not change the
OptiX claim path.

## Evidence Used

| Evidence | Path | Result |
| --- | --- | --- |
| RTX artifact | `docs/reports/cloud_2026_04_25/goal887_facility_service_coverage_rtx.json` | `copies=20000`, `iterations=10`, `query_count=80000`, `build_count=80000`, `threshold_reached_count=80000`, `all_queries_reached_threshold=true`, `optix_prepare_sec=6.341247741132975`, median `optix_query_sec=0.013249290641397238` |
| Same-scale CPU oracle baseline | `docs/reports/goal920_facility_service_coverage_cpu_oracle_baseline_2026-04-25.json` | `copies=20000`, `customer_count=80000`, `covered_customer_count=80000`, `all_customers_covered=true`, `uncovered_customer_ids=[]` |
| Parity check | local JSON comparison | CPU oracle coverage decision matches RTX threshold result and counts. |

## Promotion Decision

`facility_knn_assignment` is promoted only for the bounded
`coverage_threshold_prepared` service-coverage decision path:

- `optix_app_benchmark_readiness`: `ready_for_rtx_claim_review`
- `rt_core_app_maturity`: `rt_core_ready`
- Active manifest entry: `scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --skip-validation`

## Boundaries

- This is not a ranked nearest-depot assignment claim.
- This is not a KNN fallback assignment claim.
- This is not a facility-location optimizer claim.
- No new paid pod is needed only for this app; future reruns should happen
  only inside a consolidated regression batch.
