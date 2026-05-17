# Goal2298: Closed-Shape GEOS Toggle Negative Probe

Status: rejected optimization idea.

## Purpose

Goal2295 showed that prepared closed-shape membership spends measurable time in
host exact refinement. Goal2298 tested a narrow idea: keep the default GEOS
prepared-polygon exact refinement as the baseline, then disable it and use the
native fallback point-in-shape predicate for the exact-refine step.

The goal was to see whether GEOS overhead was the next PIP bottleneck.

## Evidence

Artifact:
`docs/reports/goal2298_closed_shape_geos_toggle_negative_probe_pod_2026-05-17.json`

Environment:

- Pod SSH: `root@69.30.85.202 -p 22064`
- Base commit: `ec0e6c96` plus a temporary local toggle patch
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`

| Mode | Median Count Seconds | Count Correct | Median Exact Refine Shape |
| --- | ---: | --- | --- |
| Default GEOS exact refine | 0.038384112 | true | about 0.004s to 0.006s |
| Host fallback exact refine | 0.039687768 | true | about 0.006s |

The fallback path preserved the expected count of `8,686`, but it was slower:
`0.967x` relative to the default GEOS path.

## Verdict

Rejected.

Do not replace the default GEOS prepared exact-refinement path with the fallback
host predicate for the current RayJoin-exported PIP stream. The measured
bottleneck remains candidate traversal/write, not GEOS exact refinement.

## Boundary

This negative probe does not authorize:

- a PIP speedup claim;
- a RayJoin reproduction claim;
- a broad GEOS-vs-fallback claim;
- true zero-copy;
- v2.0 release readiness.

The only accepted lesson is that this specific host exact-refine swap is not
worth promoting.
