# Goal3702 Segment-Pair One-Pass Exact Count Pod Validation

Date: 2026-06-07

## Purpose

Goal3701 replaced the prepared segment-pair scalar-count route with a one-pass OptiX exact-count pipeline. Goal3702 validates that route on the A5000 pod against the same-source RayJoin LSI blocker.

This is a performance-improvement validation, not a RayJoin closeout.

## Pod Setup

Artifact directory:

- `docs/reports/goal3702_segment_pair_one_pass_exact_count_pod_a5000/`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- RTDL commit: `a46ad7c4`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- RayJoin commit: `02bf622`

The pod reset RTDL to `origin/main`, rebuilt OptiX from source, and ran the same-source RayJoin probe.

## Correctness Result

Same-source LSI count remains fixed:

| Metric | Value |
| --- | ---: |
| RayJoin checked LSI count | `20860` |
| RTDL LSI scalar count | `20860` |
| RTDL minus RayJoin | `0` |

Goal3698 already proved normalized row pair-set parity for the unchanged row/witness path. Goal3702 validates the scalar-count path.

## Timing Result

| Route | RTDL query (s) | RTDL / RayJoin speedup |
| --- | ---: | ---: |
| Goal3698 corrected scalar route | `0.007232844` | `0.121x` |
| Goal3702 one-pass exact-count route | `0.004467187` | `0.199x` |

The one-pass exact-count route is about `1.62x` faster than the corrected Goal3698 route on this same-source LSI query.

Native phase telemetry for the final measured RTDL count call:

| Phase | Seconds |
| --- | ---: |
| Left upload | `0.001334103` |
| Candidate/exact count pass | `0.001033617` |
| Candidate write pass | `0.0` |
| Candidate download | `0.0` |
| Separate exact refine | `0.0` |
| Raw candidate events | `20972` |
| Emitted exact count | `20860` |

This validates the intended structural improvement: candidate row materialization and host exact refinement are gone from the scalar-count route.

## What Remains

RTDL still does not beat RayJoin on this exact same-source LSI query. RayJoin reports about `0.000899s`; RTDL reports about `0.004467s`.

The remaining gap is no longer candidate download or host exact refinement. The next measurable bottlenecks are:

- left-segment upload inside each scalar-count call,
- one OptiX launch per chunk,
- Python/ctypes/native-call overhead around a very short query,
- generic RTDL safety/accounting overhead that RayJoin's specialized C++ path does not pay.

The next useful engineering target is a prepared-left exact scalar-count route and/or a reusable resident query executor so repeated RayJoin-style queries do not re-upload the left segment set.

## Claim Boundary

This report does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

It authorizes only this internal conclusion:

```text
The app-agnostic one-pass exact segment-pair scalar-count route preserves the same-source LSI count and improves corrected RTDL LSI timing by about 1.62x on the A5000 pod, but RayJoin remains faster.
```

