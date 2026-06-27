# Goal1895 - v2 Partner Performance Matrix Status

Status: partial-matrix-pod-pending

Date: 2026-05-13

## Scope

Goal1895 summarizes the current v2.0 Python+partner+RTDL performance evidence
after the fixed-radius, segment/polygon, and road-hazard prepared-reuse work.
It is a status map, not a release claim.

## Evidence Matrix

| App path | Current best v2 partner row | RTX pod evidence | Local Linux smoke | Current status |
| --- | --- | --- | --- | --- |
| service coverage gaps | Goal1881 reusable fixed-radius output columns | `goal1881_fixed_radius_reusable_outputs_pod.json` | not needed | accepted-with-boundary |
| event hotspot screening | Goal1881 reusable fixed-radius output columns | `goal1881_fixed_radius_reusable_outputs_pod.json` | not needed | accepted-with-boundary |
| segment/polygon hitcount | Goal1886 prepared partner scene + witness outputs | `goal1886_segment_polygon_prepared_reuse_pod_512.json`, `goal1886_segment_polygon_prepared_reuse_pod_2048.json` | not needed | accepted-with-boundary |
| road hazard priority flags | Goal1889 prepared partner scene + witness outputs | pending: `goal1889_road_hazard_prepared_reuse_pod_512.json`, `goal1889_road_hazard_prepared_reuse_pod_2048.json` | `goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_64.json`, `goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_256.json` | local-smoke-pass-pod-pending |

## Known Performance Shape

The current evidence supports one engineering conclusion:

- v2.0 prepared partner reuse can remove repeated allocation/preparation costs
  and materially improve the unprepared partner path.

It does not yet support a single broad claim that v2.0 is faster than v1.8 for
every app and size. The matrix is mixed by workload, count, partner, and
baseline. For example:

- Goal1881 has strong RTX 3090 reusable-output evidence at larger fixed-radius
  sizes.
- Goal1886 beats v1.8 prepared native rows at count 2048 for segment/polygon
  hitcount, but has a small 512-row CuPy regression versus v1.8 prepared native.
- Goal1889 local GTX 1070 smoke shows prepared road-hazard partner reuse is
  faster than the Goal1869 unprepared partner path, but still needs RTX pod
  evidence before any accepted road-hazard performance wording.

## Next Pod Work

When an RTX pod is available, run:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 512 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json
python3 scripts/goal1869_road_hazard_v2_partner_perf.py \
  --count 2048 \
  --threshold 2 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json
```

After those artifacts exist, update Goal1889 and this matrix, then request
external review for the road-hazard timing row.

## Boundary

This report does not authorize v2.0 release readiness, whole-app speedup,
broad RT-core speedup, package-install support, or arbitrary PyTorch/CuPy
acceleration claims.
