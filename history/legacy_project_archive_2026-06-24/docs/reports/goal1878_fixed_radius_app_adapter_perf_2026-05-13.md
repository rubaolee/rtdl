# Goal1878 - Fixed-Radius App Adapter Timing

Status: measured-with-boundary

Date: 2026-05-13

## Scope

Goal1878 measures the Goal1877 fixed-radius app adapters on the RTX pod:

- `service_coverage_gap_flags_optix_partner_device_columns(...)`
- `event_hotspot_flags_optix_partner_device_columns(...)`

Baselines:

- v1.8 prepared OptiX fixed-radius count-threshold path with host-packed query
  rows;
- Goal1873 PyTorch/CuPy partner-reference tensor path;
- Goal1877 native OptiX partner device-column path.

Artifact:

`docs/reports/goal1878_fixed_radius_app_adapter_perf_pod.json`

## Pod Result Summary

Pod:

- SSH target: `root@213.192.2.116 -p 40189`
- checkout: `/root/rtdl`
- base commit: `0c104044`

Median seconds, 5 repeats:

| Partner | Size | App | v1.8 prepared OptiX | Goal1873 partner reference | Goal1877 native OptiX partner |
| --- | ---: | --- | ---: | ---: | ---: |
| torch | 256 | service_coverage_gaps | 0.000847 | 0.000256 | 0.000659 |
| torch | 256 | event_hotspot_screening | 0.000930 | 0.000189 | 0.000584 |
| torch | 1024 | service_coverage_gaps | 0.002618 | 0.000246 | 0.000652 |
| torch | 1024 | event_hotspot_screening | 0.003116 | 0.000204 | 0.000580 |
| cupy | 256 | service_coverage_gaps | 0.000866 | 0.000261 | 0.000635 |
| cupy | 256 | event_hotspot_screening | 0.000962 | 0.000206 | 0.000582 |
| cupy | 1024 | service_coverage_gaps | 0.002668 | 0.000223 | 0.000614 |
| cupy | 1024 | event_hotspot_screening | 0.003032 | 0.000206 | 0.000577 |

## Interpretation

The Goal1877 native OptiX partner path is faster than the v1.8 prepared
host-packed OptiX baseline on this synthetic timing harness.

The Goal1873 partner-reference tensor path is still faster than native OptiX on
these small dense point fixtures. This is not surprising: the fixture is simple
and the native path still pays OptiX GAS and launch overhead. These numbers do
not authorize broad RT-core speedup wording.

## Boundary

This is an early exact-subpath timing result only. It does not authorize:

- v2.0 release readiness;
- whole-app speedup wording;
- broad RT-core speedup wording;
- arbitrary PyTorch/CuPy acceleration wording;
- package-install wording.

The next useful performance step is larger and more realistic fixed-radius
fixtures, plus a prepared-scene app API if repeated-query timing becomes the
dominant use case.
