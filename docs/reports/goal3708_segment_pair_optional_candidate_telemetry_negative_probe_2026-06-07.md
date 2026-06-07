# Goal3708 Segment-Pair Optional Candidate Telemetry Negative Probe

Date: 2026-06-07

## Purpose

Goal3707 made candidate-event telemetry optional in the exact-count pipeline. Goal3708 tests whether disabling that diagnostic atomic helps the prepared-left same-source RayJoin LSI route.

Result: it does not help, so the telemetry-disabled form is not selected.

## Pod Result

Artifact:

- `docs/reports/goal3708_segment_pair_optional_candidate_telemetry_negative_pod_a5000/summary.json`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- RTDL commit under test: `c9305425`

Correctness remains fixed:

| Metric | Value |
| --- | ---: |
| RayJoin checked LSI count | `20860` |
| RTDL LSI scalar count | `20860` |
| RTDL minus RayJoin | `0` |

Timing regressed relative to Goal3705:

| Route | RTDL query (s) | RTDL / RayJoin speedup |
| --- | ---: | ---: |
| Goal3705 telemetry-enabled prepared-left route | `0.001086413` | `0.834x` |
| Goal3708 telemetry-disabled prepared-left probe | `0.001129784` | `0.777x` |

Native phase telemetry confirms candidate-event telemetry was disabled:

| Field | Value |
| --- | ---: |
| `raw_candidate_count` | `0` |
| `left_upload` | `0.0` |
| `candidate_write_pass` | `0.0` |
| `candidate_download` | `0.0` |
| `exact_refine` | `0.0` |

## Decision

Restore the selected prepared-left scalar-count route to telemetry-enabled mode. The optional no-telemetry hook remains in the implementation for controlled future probes, but it is not selected by the current route.

## Claim Boundary

This report does not authorize release, default-route promotion, RTDL-beats-RayJoin claims, RayJoin paper reproduction claims, public speedup claims, broad RT-core claims, or true-zero-copy claims.

