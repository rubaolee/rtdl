# Goal3705 Segment-Pair Prepared-Left Exact Count Pod Validation

Date: 2026-06-07

## Purpose

Goal3704 added a generic prepared-left scalar-count route for segment-pair exact counts. Goal3705 validates that route on the A5000 pod against the same-source RayJoin LSI blocker.

This is a performance-improvement validation, not a RayJoin closeout.

## Pod Setup

Artifact directory:

- `docs/reports/goal3705_segment_pair_prepared_left_exact_count_pod_a5000/`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- RTDL commit: `d9ec70b3`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- RayJoin commit: `02bf622`

The pod reset RTDL to `origin/main`, rebuilt OptiX from source, ran focused tests, then ran the same-source RayJoin probe.

## Correctness Result

Same-source LSI count remains fixed:

| Metric | Value |
| --- | ---: |
| RayJoin checked LSI count | `20860` |
| RTDL prepared-left LSI scalar count | `20860` |
| RTDL minus RayJoin | `0` |

## Timing Result

| Route | RTDL query (s) | RTDL / RayJoin speedup |
| --- | ---: | ---: |
| Goal3698 corrected scalar route | `0.007232844` | `0.121x` |
| Goal3702 one-pass exact-count route | `0.004467187` | `0.199x` |
| Goal3705 prepared-left exact-count route | `0.001086413` | `0.834x` |

Goal3705 is about:

- `6.66x` faster than the Goal3698 corrected route,
- `4.11x` faster than the Goal3702 one-pass route,
- still about `1.20x` slower than RayJoin on this same-source query.

Native phase telemetry for the final measured RTDL count call:

| Phase | Seconds |
| --- | ---: |
| Left upload | `0.0` |
| Candidate/exact count pass | `0.000940655` |
| Candidate write pass | `0.0` |
| Candidate download | `0.0` |
| Separate exact refine | `0.0` |
| Raw candidate events | `20972` |
| Emitted exact count | `20860` |

This validates the intended structural improvement: repeated scalar-count queries can keep both segment sets resident and avoid both candidate materialization and per-query left upload.

## Interpretation

The RayJoin same-source LSI gap is now precise:

- correctness is fixed,
- host exact refinement is removed,
- candidate row materialization is removed,
- per-query left upload is removed,
- RTDL is now close to RayJoin query timing but still slower.

The remaining gap is primarily the generic one-pass exact OptiX traversal plus Python/ctypes/native-call overhead around a very short query. A further win likely needs a reusable native repeated-query executor, lower launch/API overhead, or a hybrid exactness strategy that avoids running double arithmetic for every conservative candidate while preserving the same exact-count contract.

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
The app-agnostic prepared-left exact segment-pair scalar-count route preserves the same-source LSI count and improves corrected RTDL LSI timing to 0.834x of RayJoin on the A5000 pod, but RayJoin remains faster.
```

