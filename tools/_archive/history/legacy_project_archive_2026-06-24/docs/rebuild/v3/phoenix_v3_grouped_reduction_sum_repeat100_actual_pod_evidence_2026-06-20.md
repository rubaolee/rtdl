# Phoenix V3 Grouped-Reduction Sum Actual Repeat100 Pod Evidence

Status: `grouped_reduction_sum_repeat100_actual_pod_evidence_not_release`.

This packet supersedes the earlier modeled repeat100 candidate values for
grouped_sum, but it is now itself superseded by the scalar-broadcast optimized
repeat100 packet. It is not release authorization.

Current candidate values are in:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md
```

Source artifact directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_repeat100_actual_20260620
```

Clean 524,288-row rerun artifact directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_repeat100_actual_524288_clean_20260620
```

Machine-readable packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.json
```

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

Actual repeat=100 measurement strengthens the 262,144-row grouped_sum candidate
and weakens the 524,288-row end-to-end story once cold prepare is included.

Do not use the older modeled 32x/33x repeat100 values as current candidate
wording.

Fresh external review for the current optimized packet is currently blocked:

```text
docs/reviews/external_review_blocked_phoenix_v3_grouped_reduction_scalar_broadcast_optimization_2026-06-20.md
```

## Pre-Optimization Measured Rows

| Row | Rows | Groups | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Embree loop | OptiX loop | Classification |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `grouped_reduction_sum_repeat100_actual_262144` | 262,144 | 1,024 | 197.056x | 199.501x | 27.012x | 101.032s | 0.506s | actual repeat100 candidate, not M7 |
| `grouped_reduction_sum_repeat100_actual_524288` | 524,288 | 2,048 | 157.203x | 155.547x | 2.062x | 207.336s | 1.333s | candidate with clean-confirmed large cold prepare cost, not M7 |

Cold prepare is part of the user contract:

| Row | Embree cold plus loop | OptiX cold plus loop |
| --- | ---: | ---: |
| `grouped_reduction_sum_repeat100_actual_262144` | 102.940s | 3.811s |
| `grouped_reduction_sum_repeat100_actual_524288` | 388.026s | 188.185s |

## What Changed

The previous candidate wording used a formula projection from measured cold
prepare plus 100 times hot-query median. That was disclosed, but it was still a
weaker basis than a direct repeat=100 run.

The pre-optimization direct repeat=100 run found:

- 262,144-row grouped_sum remains strong after cold prepare: 27.012x.
- 524,288-row grouped_sum is not a 33x end-to-end row after cold prepare:
  2.062x in the clean rerun.

So V3 candidate wording must use actual repeat100 values, not the older modeled
values. After this packet, a generic scalar-broadcast packer optimization was
implemented and rerun; current candidate wording must use that later optimized
evidence.

## Artifact Note

The first background launch used incorrect PowerShell quoting. As a result, the
finished JSON/log/gate files were initially written under remote `/`. They were
moved after completion into the intended artifact directory listed above. The
measurement commands still ran from:

```text
/root/rtdl_v3_rebuild_20260620/current
```

against:

```text
scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
```

The preserved log is:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_repeat100_actual_20260620/repeat100_actual.log
```

Because that first launch had an artifact-placement quoting mistake, the
524,288-row case was rerun cleanly with correct quoting. The clean rerun
confirmed the large cold prepare cost and is the current source for the
524,288-row candidate numbers:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_repeat100_actual_524288_clean_20260620/grouped_sum_repeat100_actual_524288_clean.json
```

## Forbidden Public Reading

- Do not claim V3 is 224x faster from grouped_reduction.
- Do not claim RTDL is 33x faster end to end from the old modeled repeat100
  packet.
- Do not hide cold prepare cost.
- Do not call either row M7-qualified before external public-row review.

## Goal-Level Decision Audit

Decision: replace grouped_sum modeled repeat100 candidate values with actual
repeat100 pod evidence.

1. Did I make a foolish decision?

   Partly. The previous modeled wording was disclosed, but keeping it after pod
   access would be too weak for Phoenix V3.

2. If yes, what actions made the decision foolish?

   The foolish action would be to leave 32x/33x modeled repeat100 as current
   candidate wording after actual repeat100 showed 27.012x and a
   clean-confirmed 2.062x cold-plus-loop speedup.

3. Was there another path?

   Yes. Wait for external review of the modeled packet. That would preserve a
   known measurement gap.

4. Can I now try a different path that truly solves the problem?

   Yes. Use actual repeat100 evidence, use the clean 524,288-row rerun for
   that scale, keep release authorization false, and request external review
   when Claude or another reviewer is available.
