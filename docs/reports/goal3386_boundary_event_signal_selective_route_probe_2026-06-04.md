# Goal3386 - Boundary-Event Signal Selective Route Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3383 showed that topology-only ambiguity signals are not safe as a default
owner-face route. Goal3385 added a generic selective boundary-event CuPy filter.

Goal3386 combines both directions:

1. Use live OptiX candidate device columns.
2. Use live OptiX first-boundary-event device columns.
3. Derive selected points from generic topology plus strict zero-boundary
   candidate counts.
4. Run the generic selective boundary-event CuPy filter only on those selected
   points.
5. Compare the final row set against a live exact OptiX oracle.

Exact output is used only for evaluation, not as an input to the selection
signal.

## Evidence

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit: `8f2660556ac28b37f8b9114bac930962f27720b2`

Artifact:
`docs/reports/goal3386_boundary_event_signal_selective_route_probe_2026-06-04.json`

## Signal

The selected-point signal is:

```text
candidate_count > zero_boundary_candidate_count
and zero_boundary_candidate_count == 2
and incident_row_count == 3
and candidate_face_count == 4
```

The signal selected:

```text
522, 523, 538, 539, 540, 564, 565
```

Those are exactly the true candidate-extra points for this 512-chain slice.

## Result

| Measure | Value |
| --- | ---: |
| Live OptiX candidate rows | 1429 |
| Live OptiX boundary-event rows | 4836 |
| Live exact rows | 1417 |
| Candidate extras before filter | 12 |
| Selected points | 7 |
| Selected candidate rows | 26 |
| Selected kept rows | 14 |
| Selected dropped rows | 12 |
| Passthrough candidate rows | 1403 |
| Filtered rows | 1417 |
| Missing exact rows | 0 |
| Extra rows | 0 |
| Full-slice match | true |

## Interpretation

This is a constructive improvement over Goal3381:

- Goal3381 required the caller to provide the seven mismatch point ids.
- Goal3386 derives the same seven ids from live generic boundary-event columns
  plus CDB-derived generic topology features.
- The native engine stays app-agnostic.
- The continuation remains a Python/CuPy composition over generic columns.

This is not yet a default route. The signal is validated on one bounded
512-chain county slice only. It needs larger CDB slices and additional dataset
families before it can graduate from a bounded signal candidate to a default
front door.

## Boundary

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route
claims. All artifact claim-boundary flags remain false.
