# Goal2305 Current RayJoin-Style Prepared Comparison After Bounded Probe

Date: 2026-05-17

## Purpose

Goal2292 refreshed the current RTDL prepared RayJoin-style comparison after the
packed-left direct-index LSI work. Goal2301/Goal2303 then changed the current
PIP-style path by replacing the infinite closed-shape point probe with a
bounded generic point/closed-shape probe.

This report refreshes the current comparison table so future readers do not
mistake the pre-Goal2301 PIP numbers for the current state.

## Evidence

Artifact:

- `docs/reports/goal2305_rayjoin_current_prepared_comparison_after_bounded_probe_pod_2026-05-17.json`

Source artifact:

- `docs/reports/goal2301_bounded_point_probe_candidate_pod_2026-05-17.json`

Pod:

- SSH: `root@69.30.85.202 -p 22064`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Candidate commit: `c84f52193b99337ba88c6d09543d286209f2247c`
- Runtime source-tree style: `PYTHONPATH=src:.`
- OptiX library:
  `/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so`

The artifact uses the RayJoin-exported 100,000-query streams from the earlier
same-query pod lane:

- LSI stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_lsi_gen100000_stream.json`
- PIP stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`

## Current Table

| Workload route | Current RTDL path | Median seconds | Exact expected count |
| --- | --- | ---: | ---: |
| LSI raw rows | prepared segment-pair intersection with prepacked left | 0.008976681 | 8,921 |
| LSI scalar count | prepared segment-pair scalar count with prepacked left | 0.008994997 | 8,921 |
| PIP positive rows | prepared point/closed-shape membership with bounded probe | 0.023158047 | 8,686 |
| PIP scalar count | prepared point/closed-shape scalar count with bounded probe | 0.009362523 | 8,686 |

## Interpretation

LSI remains on the accepted prepared segment-pair path from Goal2289/Goal2292.
PIP now uses the accepted bounded point/closed-shape probe from
Goal2301/Goal2303.

The biggest current improvement is the PIP scalar-count path. The clean
committed run preserves exact count parity while reducing the measured median
from the pre-Goal2301 current baseline `0.037854942 s` to `0.009362523 s`
on the same 100,000-query stream.

## Boundary

This report is a current RTDL internal comparison refresh only.

Not claimed:

- No RayJoin paper reproduction.
- No claim that RTDL beats RayJoin.
- No broad whole-app speedup claim.
- No true zero-copy claim.
- No v2.0 release authorization.
- The bounded probe half-length is still validated only for the current
  RayJoin-exported coordinate scale.

