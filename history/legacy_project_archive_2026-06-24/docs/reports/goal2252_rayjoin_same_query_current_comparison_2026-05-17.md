# Goal2252: RayJoin Same-Query Current Comparison

Status: evidence recorded; review pending.

## Purpose

Goal2252 refreshes the current RTDL OptiX same-query RayJoin learner comparison
after Goal2248/2249 added prepared closed-shape membership for the PIP route.

The purpose is not to claim RTDL reproduces or beats RayJoin. The purpose is to
keep the current v2.0 learner implementation traceable against the RayJoin paper
workload shape: a RayJoin-exported 100,000-query stream, exact row parity, and a
visible Python+RTDL runtime boundary.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Pod checkout: `/root/rtdl_goal2198_launcher/rtdl`
- Commit: `949ca4f60a19b61bade10682d17a645bc07ec588`
- GPU: NVIDIA RTX A5000, driver `570.211.01`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`
- LSI stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_lsi_gen100000_stream.json`
- PIP stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`

## Current Results

Each row used one warmup and nine timed repeats. Both artifacts report exact
parity against the RTDL CPU reference.

| Workload | RTDL route | Queries | Rows | Median seconds | Parity |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | `compiled_rtdl_kernel` | 100,000 | 8,921 | 0.08359288796782494 | true |
| PIP | `prepared_closed_shape_membership_2d_optix` | 100,000 | 8,686 | 0.06329288892447948 | true |

Artifacts:

- `docs/reports/goal2252_rayjoin_lsi_current_same_query_pod_2026-05-17.json`
- `docs/reports/goal2252_rayjoin_pip_current_same_query_pod_2026-05-17.json`

## Interpretation

The main improvement is that PIP no longer pays repeated closed-shape scene
preparation in the measured loop. It is now faster than the LSI row in this
Python+RTDL harness, and it stays within the app-agnostic primitive vocabulary:
point, closed shape, membership, prepared scene.

The remaining RayJoin gap is expected and should be described honestly:

- RayJoin's paper implementation reports a tight native GPU query metric.
- This RTDL learner harness measures a Python-visible runtime call that returns
  host rows and preserves the language boundary.
- Goal2249/2252 therefore support a v2.0 design lesson, not a RayJoin-beat
  claim.

## Boundary

This report does not authorize:

- full RayJoin reproduction,
- a claim that RTDL beats RayJoin,
- paper-scale RayJoin speedup claims,
- broad LSI or PIP speedup claims,
- or v2.0 release readiness.

The actionable next idea is already captured in
`docs/research/future_version_to_do_list.md`: prepared scenes plus
device-resident output streams are likely needed to approach RayJoin's pure
query-execution contract without hiding app logic inside the RTDL engine.
