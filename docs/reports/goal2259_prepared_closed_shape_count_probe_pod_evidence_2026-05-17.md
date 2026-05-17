# Goal2259: Prepared Closed-Shape Count Probe Pod Evidence

Status: evidence recorded; review pending.

## Purpose

Goal2258 added a generic count-only method for prepared closed-shape membership.
Goal2259 records pushed-commit pod evidence for that method on the RayJoin
same-query PIP learner stream.

The tested surface is generic:

```text
rtdl_optix_count_prepared_point_closed_shape_membership_2d
PreparedOptixPointClosedShapeMembership2D.count(...)
```

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Commit: `73f58a059e393788cf48b66694223c2c08944dd3`
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
PYTHONPATH=src:. python3 -m unittest tests.goal2258_prepared_closed_shape_membership_count_mode_test
Ran 3 tests: OK
```

## Timing Result

The probe used one warmup and nine timed repeats for each path on the same
prepared scene and prepacked point stream.

Artifact:
`docs/reports/goal2259_prepared_closed_shape_count_probe_pod_2026-05-17.json`

| Path | Median seconds | Count | Reference match |
| --- | ---: | ---: | --- |
| `prepared.run(...)` row return | 0.05280204117298126 | 8,686 | true |
| `prepared.count(...)` count return | 0.041955990716814995 | 8,686 | true |

The count path is about `1.26x` faster than row-return materialization within
this probe.

## Interpretation

This validates the expected v2.0 language/runtime lesson: when the user wants a
generic count reduction, returning a scalar count avoids Python dictionary row
materialization and is measurably faster, while keeping the native engine
app-agnostic.

This is still not the final RayJoin pure-GPU metric. The implementation reuses
the exact prepared membership path and returns a host scalar; it does not yet
provide a fully device-resident downstream partner stream.

## Boundary

This report does not authorize:

- a claim that RTDL beats RayJoin,
- paper-scale RayJoin speedup claims,
- broad PIP speedup claims,
- v2.0 release readiness,
- or a true device-resident output-stream claim.
