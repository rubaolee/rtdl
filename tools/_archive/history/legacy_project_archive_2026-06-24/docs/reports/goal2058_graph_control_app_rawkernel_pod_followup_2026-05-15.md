# Goal2058 Graph Control-App RawKernel Pod Follow-Up

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2058 isolates the graph control app after Goal2056 showed that `copies=4096` made the v1.8 graph baseline too long for an all-app blocking run.

The purpose is to get a completed pod artifact at a bounded size, not to claim that v2.0 has a reusable general graph primitive yet.

## Pod Result

Artifact:

- `docs/reports/goal2058_graph_rawkernel_cupy_optix_l4_512.json`

Command shape:

```bash
timeout 600 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1955_rawkernel_control_app_perf.py \
  --apps graph_analytics \
  --copies 512 \
  --partner cupy \
  --candidate-backend optix \
  --repeats 3 \
  --warmups 1 \
  --source-commit-label 2feec1a4-pod-graph-512
```

Result:

| App | Copies | v1.8 median | v2 median | Ratio |
| --- | ---: | ---: | ---: | ---: |
| graph_analytics | 512 | 5.206507 | 0.000121 | 0.000023x |

Correctness:

- `all_match_v1_8_python_rtdl_oracle`: `true`
- `matches_v1_8_python_rtdl_oracle`: `true`

The payload summaries match for:

- BFS discovered edges/vertices/max level;
- triangle count and touched vertices;
- visibility visible/blocked edge counts.

## Interpretation

This is strong evidence that the authored v2 graph control app can avoid the v1.8 row-materialization path for this synthetic graph workload.

It is not yet evidence of a reusable general graph primitive. The current v2 graph control implementation is a closed-form/rawkernel continuation for the authored app shape. The v2.0 design still needs a traceable reusable graph continuation contract if we want to claim broad graph programmability beyond this control app.

## Boundary

Allowed claim:

- On the L4 pod, the authored v2 graph control app is much faster than the v1.8 Python+RTDL baseline at `copies=512`.
- Correctness parity holds for the authored graph summary.

Not allowed:

- reusable general graph primitive readiness;
- v2.0 release readiness;
- broad all-app speedup;
- graph `copies=4096` completion;
- broad RT-core speedup;
- package-install readiness.

## Verdict

`accept-with-boundary`
