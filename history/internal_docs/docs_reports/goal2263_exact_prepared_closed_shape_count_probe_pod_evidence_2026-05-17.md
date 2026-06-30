# Goal2263: Exact Prepared Closed-Shape Count Probe Pod Evidence

Status: evidence recorded; review pending.

## Purpose

Goal2262 changed the prepared closed-shape count implementation so it no longer
calls the row-return path or allocates final membership rows just to count them.
Goal2263 records pushed-commit pod evidence for that exact count path.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Commit: `4f03c1cb5d9bedc18963d07df49220fc38f3e4c4`
- GPU: NVIDIA RTX A5000, driver `570.211.01`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`
- Query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`

## Validation

The pod was reset to `origin/main`, rebuilt, and tested:

```text
git fetch origin main
git reset --hard origin/main
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2262_exact_prepared_closed_shape_count_without_final_rows_test \
  tests.goal2258_prepared_closed_shape_membership_count_mode_test
Ran 6 tests: OK
```

## Timing Result

Artifact:
`docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_2026-05-17.json`

The probe used one warmup and eleven timed repeats for each path on the same
prepared scene and prepacked point stream.

| Path | Median seconds | Count | Reference match |
| --- | ---: | ---: | --- |
| `prepared.run(...)` row return | 0.055270278826355934 | 8,686 | true |
| `prepared.count(...)` exact scalar count | 0.04043779522180557 | 8,686 | true |

The exact scalar count path is about `1.37x` faster than row-return
materialization in this pushed-commit probe.

Compared with Goal2259's first count evidence (`0.041955990716814995` seconds),
Goal2263 is about `1.04x` faster. That is a small timing improvement, but it is
an important semantic cleanup: count mode now directly counts exact hits instead
of producing final rows and freeing them.

## Interpretation

The useful v2.0 lesson is that generic reduction-style outputs should be first-
class runtime surfaces. If a learner asks for a count, the runtime should not
force Python-visible row materialization. This keeps the engine app-agnostic and
matches the stable RTDL primitive direction of generic integer reductions.

This still is not a true device-resident output stream. The exact count path
keeps host-side exact refinement and returns a host scalar.

## Boundary

This report does not authorize:

- a claim that RTDL beats RayJoin,
- paper-scale RayJoin speedup claims,
- broad PIP speedup claims,
- v2.0 release readiness,
- or a true device-resident output-stream claim.
