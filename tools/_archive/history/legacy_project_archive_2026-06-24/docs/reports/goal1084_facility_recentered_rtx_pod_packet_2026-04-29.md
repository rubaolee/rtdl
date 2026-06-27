# Goal1084 Facility Recentered RTX Pod Packet

Date: 2026-04-29

Valid: `true`

Goal1084 prepares a corrected facility RTX pod run only. It does not create cloud resources, does not run cloud locally, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Build the OptiX backend from the checked-out commit before commands.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Do not add --skip-validation. If validation is too expensive, copy back the partial artifact and stop.
- Treat this as evidence collection only; no public wording changes are authorized by this runner.

## Rows

| App | Path | Phase | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `same_scale_validation_and_timing` | `False` | `0.100` | `docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage_recentered --mode optix --copies 2500000 --iterations 5 --radius 1.0 --output-json docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` |

## Boundary

Goal1084 prepares a corrected facility RTX pod run only. It does not create cloud resources, does not run cloud locally, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
