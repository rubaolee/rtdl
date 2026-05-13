# Goal1863 - Segment/Polygon Hitcount v2 Partner Timing Row

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1863 adds a narrow timing harness for the second app-level v2.0 partner row:

`scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`

The measured app is `segment_polygon_hitcount`. The comparison is:

- v1.8/current one-shot native OptiX row path:
  `rt.run_optix(segment_polygon_hitcount_reference, ...)`
- v1.8/current prepared native OptiX row path:
  `prepare_optix_segment_polygon_hitcount_2d(...).run(...)`
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

| Path | Median query time (s) | Ratio vs v1.8 one-shot | Ratio vs v1.8 prepared |
| --- | ---: | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | 0.1764944121 | 1.000x | 186.719x |
| v1.8 prepared native OptiX hitcount rows | 0.0009452328 | 0.0054x | 1.000x |
| v2.0 CuPy device count columns | 0.0014976561 | 0.0085x | 1.584x |
| v2.0 Torch device count columns | 0.0013628453 | 0.0077x | 1.442x |

The same harness should also run at 2048 rows:

| Path | Median query time (s) | Ratio vs v1.8 one-shot | Ratio vs v1.8 prepared |
| --- | ---: | ---: | ---: |
| v1.8 one-shot native OptiX hitcount rows | 14.7081498653 | 1.000x | 4436.663x |
| v1.8 prepared native OptiX hitcount rows | 0.0033151358 | 0.00023x | 1.000x |
| v2.0 CuPy device count columns | 0.0014812797 | 0.00010x | 0.447x |
| v2.0 Torch device count columns | 0.0012702122 | 0.00009x | 0.383x |

The first partner iteration includes one-time framework/kernel effects and is
retained in the artifact rather than hidden. The median is the working
comparison statistic for this narrow row.

Column-build phase:

- 512 rows: CuPy 0.0044035688 s, Torch 0.0147466883 s
- 2048 rows: CuPy 0.0070588440 s, Torch 0.0181888342 s

The one-shot v1.8 native hitcount baseline is unexpectedly expensive at 2048
synthetic rows because it includes the public one-shot app path. The prepared
v1.8 native baseline is the fairer repeated-query comparison: v2.0 is slower at
512 rows but faster at 2048 rows in this synthetic setup. These rows are useful
engineering evidence, but they should be treated as a review target rather than
immediate public speedup wording.

## Boundary

This is a same-contract v2.0-vs-v1.8 timing row for one app path. It is not an all-app performance table and does not authorize v2.0 release wording.

No whole-app speedup claim, broad RT-core speedup claim, package-install claim,
or v2.0 release claim is authorized by this goal.
