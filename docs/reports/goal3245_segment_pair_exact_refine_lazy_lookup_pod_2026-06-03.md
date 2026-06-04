# Goal3245: Segment-Pair Exact-Refine Lazy Lookup Pod Evidence

Date: 2026-06-03

## Purpose

Goal3244 showed that RTDL's same-slice prepared OptiX LSI count path was still
about `6.20x` slower than upstream RayJoin's RT `query_exec` timing on the
bounded public CDB slice. The phase telemetry made the bottleneck precise:
RTDL spent about `1.121 ms` in host exact refine after RT-core candidate
discovery.

Goal3245 made one low-risk native change: the segment-pair exact-refine code no
longer builds `left_by_id` and `right_by_id` hash maps on every query when the
GPU candidate row already carries valid left/right indices. The fallback ID
lookup path remains available, and exact segment intersection plus pair dedupe
remain unchanged.

## Artifacts

- Native guard test: `tests/goal3245_segment_pair_exact_refine_lazy_lookup_test.py`
- Pod JSON: `docs/reports/goal3245_segment_pair_lazy_lookup_pod_2026-06-03.json`
- Pod stdout: `docs/reports/goal3245_segment_pair_lazy_lookup_pod_2026-06-03.stdout`
- RayJoin process logs: `docs/reports/goal3245_segment_pair_lazy_lookup_pod/`

Pod evidence was collected on an NVIDIA A40 with driver `570.211.01`.
The RTDL commit under test was `92082014ce40c596669edc47c7338ecb4e4c125f`.
The source tree reported by the runner was clean.

## Same-Slice Results

| Workload | RayJoin RT query median | RTDL prepared count median | RTDL/RayJoin | Count status |
| --- | ---: | ---: | ---: | --- |
| LSI | 0.232999 ms | 0.401776 ms | 1.72x | visible count matches: 269 vs 269 |
| PIP | 0.193596 ms | 1.147646 ms | 5.93x | RTDL count 1430; RayJoin count not printed |

## Before And After

| Workload | Goal3244 RTDL median | Goal3245 RTDL median | RTDL improvement | Gap before | Gap after |
| --- | ---: | ---: | ---: | ---: | ---: |
| LSI | 1.449205 ms | 0.401776 ms | 3.61x | 6.20x | 1.72x |
| PIP | 1.116930 ms | 1.147646 ms | 0.97x | 5.76x | 5.93x |

The LSI win is the intended effect of the lazy lookup change. PIP was not a target
of this goal and remained essentially unchanged within run noise.

## Phase Diagnosis

For LSI, the median exact-refine phase dropped from about `1.121 ms` in
Goal3244 to about `0.041 ms` in Goal3245. The remaining native phases are now
mostly:

- candidate count pass: about `0.097 ms`
- candidate write pass: about `0.053 ms`
- candidate download: about `0.011 ms`
- exact refine: about `0.041 ms`

This confirms that the previous LSI gap was mostly avoidable host hash-map
construction in the exact-refine authority path, not RT traversal itself.

For PIP, the median candidate/write traversal remains about `0.948 ms`, with
exact refine at about `0.085 ms`. The next PIP target is therefore a generic
count-only closed-shape membership path that can avoid writing and downloading a
candidate row stream when the requested result is only a count.

## Boundary

Goal3245 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The narrow conclusion is that RTDL's prepared OptiX LSI count path is now much
closer to upstream RayJoin on this bounded public same-slice query, while PIP
still needs a separate count-only path.
