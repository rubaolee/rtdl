# Goal3248: RayJoin Current Best After LSI Lazy Lookup And PIP Extent Tuning

Date: 2026-06-03

## Purpose

Goal3245 improved the LSI prepared OptiX count path by removing avoidable
per-query hash-map construction from segment-pair exact refine. Goal3247 added
and measured a generic closed-shape probe half-extent override; on the bounded
public PIP same-slice workload, `0.25` preserved the default count and improved
PIP query time.

Goal3248 records the combined current-best same-slice comparison:

- LSI: default prepared segment-pair count with Goal3245 lazy lookup.
- PIP: prepared closed-shape membership count with
  `RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25`.

## Artifacts

- Pod JSON: `docs/reports/goal3248_rayjoin_current_best_extent025_pod_2026-06-03.json`
- Pod stdout: `docs/reports/goal3248_rayjoin_current_best_extent025_pod_2026-06-03.stdout`
- RayJoin process logs: `docs/reports/goal3248_rayjoin_current_best_extent025_pod/`

The pod run used commit `eb09b9b21a7e6223fd96769326331216fe609035` and reported
a clean source tree.

## Results

| Workload | RayJoin RT query median | RTDL current-best median | RTDL/RayJoin | Count status |
| --- | ---: | ---: | ---: | --- |
| LSI | 0.232792 ms | 0.458829 ms | 1.97x | visible count matches: 269 vs 269 |
| PIP | 0.193803 ms | 0.934755 ms | 4.82x | RTDL count 1430; RayJoin count not printed |

Compared with Goal3244's first repeated baseline:

| Workload | Goal3244 RTDL median | Goal3248 RTDL median | RTDL improvement | Gap before | Gap now |
| --- | ---: | ---: | ---: | ---: | ---: |
| LSI | 1.449205 ms | 0.458829 ms | 3.16x | 6.20x | 1.97x |
| PIP | 1.116930 ms | 0.934755 ms | 1.19x | 5.76x | 4.82x |

The LSI number is noisier than the best Goal3245 run (`0.401776 ms`) but still
confirms the large lazy-lookup improvement. The PIP number is consistent with
Goal3247's extent sweep and is now the current bounded same-slice PIP best.

## Remaining Bottleneck

The current PIP median native phases are:

- candidate/write traversal: about `0.735 ms`
- exact refine: about `0.085 ms`
- candidate download: about `0.013 ms`
- point upload: about `0.026 ms`

So PIP is still mostly a traversal/predicate problem, not a host exact-refine or
row-download problem. The old ray/segment-group parity route is not a drop-in
solution because it materializes segment-pair rows and groups on the host. The
next RayJoin-level engineering target is a generic device-resident grouped
parity/count primitive, or another closed-shape membership primitive that avoids
the probe-extent heuristic.

## Boundary

Goal3248 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The narrow conclusion is that RTDL's current generic prepared OptiX count paths
are now much closer for LSI and modestly better for PIP, while upstream RayJoin
remains faster on both bounded same-slice query/count comparisons.
