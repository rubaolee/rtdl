# Phoenix V3 RTDBSCAN Continuation-Bottleneck No-Go

Status: `rtdbscan_continuation_bottleneck_no_go_not_promoted`.

This packet closes the current RTDBSCAN pass without M7 promotion. It is not a
release report and not public speedup wording.

## Bottom Line

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_external_review_status: blocked_current_packet
current_packet_2ai_consensus_status: not_recorded_for_this_packet
```

RTDBSCAN has useful internal V3 evidence, but current evidence does not provide
an M7 row. The fair same-contract comparison shows only small overall
OptiX-over-Embree wins, while the shared Numba continuation dominates the large
OptiX cases. The stronger M23 grouped-stream component-signature row is a
different contract and cannot be pasted onto the same-contract comparison.

## Same-Contract Evidence

Source:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_same_contract_20260620_fresh/summary.json
docs/rebuild/v3/phoenix_v3_rtdbscan_same_contract_pod_evidence_2026-06-20.md
```

| Points | Overall OptiX/Embree | RT-threshold phase | OptiX RT phase | OptiX continuation | Continuation / RT phase | Continuation dominates |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4,096 | 1.466x | 2.061x | 0.005601s | 0.004297s | 0.767x | false |
| 65,536 | 1.150x | 1.297x | 0.166707s | 0.137137s | 0.823x | false |
| 262,144 | 1.079x | 1.312x | 0.655499s | 1.728318s | 2.637x | true |
| 524,288 | 1.071x | 1.470x | 1.310395s | 6.906373s | 5.270x | true |

The 4,096-point control row passes CPU reference validation for both backends.
The large rows skip full CPU reference validation, but Embree and OptiX produce
the same canonical component-size signature.

## M23 Is Separate

Source:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m23_dbscan_component_signature_524288.json
```

M23 is valuable internal evidence:

| Field | Value |
| --- | --- |
| Point count | 524,288 |
| Partners | CuPy and Numba |
| Output mode | `component_signature` |
| Oracle/signature checks | true |
| Python row materialization | false |
| Native continuation active | true |
| CuPy hot component-label median | 0.000593s |
| Numba hot component-label median | 0.000668s |

But M23 is not an M7 public row because it has no same-scale Embree baseline
for the same grouped-stream component-signature contract. It must not be used
to make the same-contract RTDBSCAN row look faster.

## Current Decision

RTDBSCAN remains internal:

- Do not use the old `1483.603x` all-app row.
- Do not call component signatures full DBSCAN labels.
- Do not quote RT-threshold phase speedup as whole RTDBSCAN speedup.
- Do not mix M23 grouped-stream evidence with same-contract Numba continuation
  evidence.

## Reopen Requirements

To reopen RTDBSCAN as an M7 candidate, one of these must happen:

- optimize the shared component-signature continuation under the same
  Embree/OptiX contract and rerun the same-contract matrix;
- or add a same-scale Embree baseline for the M23 grouped-stream
  component-signature contract;
- preserve validation/signature parity and phase timing;
- obtain external review before any M7 or public speedup wording.

## External Review

Fresh external review is blocked:

```text
docs/reviews/external_review_blocked_phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: classify RTDBSCAN as no-go for M7 from current evidence and avoid a
new pod rerun until a real same-contract optimization exists.

1. Was I foolish?

   No. The current evidence already identifies the bottleneck and prevents a
   route-mixing mistake.

2. If yes, what actions made the decision foolish?

   It would be foolish to promote the old 1483.603x row, to mix M23
   grouped-stream evidence with the same-contract Numba route, or to spend pod
   time rerunning unchanged code.

3. Was there another path that would have avoided getting stuck on that idea?

   Yes. Run a new pod matrix immediately. That would not solve the measured
   continuation bottleneck without a changed same-contract implementation.

4. Can I now try a different path that actually solves the problem?

   Yes. Record the no-go boundary, gate it in tests, teach the route split, and
   move to another V3 capability or a real continuation optimization design.
