# Goal1863 - Segment/Polygon Hitcount v2 Partner Timing Row

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1863 adds a narrow timing harness for the second app-level v2.0 partner row:

`scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`

The measured app is `segment_polygon_hitcount`. The comparison is:

- v1.8/current native OptiX row path:
  `rt.run_optix(segment_polygon_hitcount_reference, ...)`
- v2.0 preview caller-supplied partner-column path:
  `segment_polygon_hitcount_optix_partner_device_count_columns`

Both paths are checked against the same `segment_id` / `hit_count` row
semantics. The v2.0 path returns partner-owned device columns and converts them
to host rows only after timing for parity validation.

## Pod Evidence

Artifacts:

`docs/reports/goal1863_segment_polygon_hitcount_v2_partner_perf_pod_512.json`

`docs/reports/goal1863_segment_polygon_hitcount_v2_partner_perf_pod_2048.json`

## Observed Timing

The timing rows are internal engineering evidence only.

Dataset: 512 synthetic segment/triangle rows, 512 expected output rows, bounded
output capacity 1024.

| Path | Median query time (s) | Ratio vs v1.8 native query |
| --- | ---: | ---: |
| v1.8 native OptiX hitcount rows | 0.1781796366 | 1.000x |
| v2.0 CuPy device count columns | 0.0013938695 | 0.0078x |
| v2.0 Torch device count columns | 0.0012617484 | 0.0071x |

The same harness should also run at 2048 rows:

| Path | Median query time (s) | Ratio vs v1.8 native query |
| --- | ---: | ---: |
| v1.8 native OptiX hitcount rows | 15.1251612604 | 1.000x |
| v2.0 CuPy device count columns | 0.0014832616 | 0.00010x |
| v2.0 Torch device count columns | 0.0012883395 | 0.00009x |

The first partner iteration includes one-time framework/kernel effects and is
retained in the artifact rather than hidden. The median is the working
comparison statistic for this narrow row.

Column-build phase:

- 512 rows: CuPy 0.1150562689 s, Torch 0.0147782564 s
- 2048 rows: CuPy 0.1205041036 s, Torch 0.0181660503 s

The v1.8 native hitcount baseline is unexpectedly expensive at 2048 synthetic
rows. This is useful engineering evidence about the current app-level native
path, but it should be treated as a review target rather than immediate public
speedup wording.

## Boundary

This is a same-contract v2.0-vs-v1.8 timing row for one app path. It is not an all-app performance table and does not authorize v2.0 release wording.

No whole-app speedup claim, broad RT-core speedup claim, package-install claim,
or v2.0 release claim is authorized by this goal.
