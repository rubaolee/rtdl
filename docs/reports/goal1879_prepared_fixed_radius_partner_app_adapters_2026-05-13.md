# Goal1879 - Prepared Fixed-Radius Partner App Adapters

Status: measured-with-boundary

Date: 2026-05-13

## Scope

Goal1879 adds reusable prepared-scene adapter helpers for the Goal1875
fixed-radius OptiX partner bridge:

- `prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(...)`
- `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(...)`
- `service_coverage_gap_flags_optix_prepared_partner_device_columns(...)`
- `event_hotspot_flags_optix_prepared_partner_device_columns(...)`

The goal is to avoid rebuilding the OptiX fixed-radius search GAS on every app
call when a workload issues repeated queries against the same search point set.

## Boundary

This is still the same generic native contract:

`generic_fixed_radius_count_threshold_2d_device_columns`

App semantics remain Python-side. This goal does not authorize v2.0 release
readiness, whole-app speedup wording, broad RT-core speedup wording, arbitrary
partner acceleration wording, or package-install wording.

## Pod Timing

Artifact:

`docs/reports/goal1879_fixed_radius_app_adapter_perf_prepared_pod.json`

Median seconds, 5 repeats:

| Partner | Size | App | Goal1877 native | Goal1879 prepared native |
| --- | ---: | --- | ---: | ---: |
| torch | 256 | service_coverage_gaps | 0.000732 | 0.000392 |
| torch | 256 | event_hotspot_screening | 0.000619 | 0.000304 |
| torch | 1024 | service_coverage_gaps | 0.000628 | 0.000328 |
| torch | 1024 | event_hotspot_screening | 0.000576 | 0.000265 |
| cupy | 256 | service_coverage_gaps | 0.000608 | 0.000294 |
| cupy | 256 | event_hotspot_screening | 0.000569 | 0.000269 |
| cupy | 1024 | service_coverage_gaps | 0.000612 | 0.000298 |
| cupy | 1024 | event_hotspot_screening | 0.002256 | 0.000264 |

Prepared native reuse cuts the per-call native timing substantially on this
fixture. The Goal1873 partner-reference tensor path remains faster on these
small dense inputs, so this is still exact-subpath evidence, not broad RT-core
speedup evidence.
