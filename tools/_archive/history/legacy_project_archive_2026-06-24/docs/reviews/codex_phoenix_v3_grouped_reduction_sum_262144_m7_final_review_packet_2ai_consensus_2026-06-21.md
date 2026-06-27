# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet

Status: Claude/Codex consensus complete for one row-scoped M7-qualified result.

## Sources

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json
docs/reviews/claude_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_review_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620/grouped_sum_scalar_broadcast_repeat100_262144.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620/source_manifest.sha256
```

## Verdict

Codex agrees with Claude's review: promote only this exact row to
M7-qualified row-scoped status:

```text
row_id: grouped_reduction_sum_scalar_broadcast_repeat100_262144
generic_capability: grouped_reduction
operation: group_sum_i64
rows: 262,144
groups: 1,024
warmup: 3
repeat: actual repeat=100
actual repeat100 loop: 200.353x
actual cold plus repeat100 loop: 27.917x
```

This consensus does not authorize a V3 release, a whole-app/database speedup
claim, a broad V3-over-V2 speedup claim, the 524,288-row sum row, or count rows.

## Claude Findings

Claude's verdict was:

```text
Option 1 - Approve as M7-qualified, subject to two P0 conditions.
```

Claude verified the arithmetic, correctness, same-contract scope, cold-prepare
disclosure, scalar-broadcast generic optimization boundary, and row exclusions.

Claude P0 conditions:

```text
P0-1: Source provenance gap (git_head is empty)
P0-2: 2-AI consensus not yet recorded
```

## Codex Resolution

P0-1 is resolved by documenting that the pod artifact has no usable git HEAD and
that `source_manifest.sha256` is the source traceability record for this row.

P0-2 is resolved by this Codex consensus record. The required 2-AI chain is:

```text
Claude external review + Codex consensus
```

Non-P0 cleanup is also accepted:

```text
row-id inconsistency: fixed by using grouped_reduction_sum_scalar_broadcast_repeat100_262144
hit-event count discrepancy: documented as pre-dedup backend traversal/order difference with CPU-reference parity
```

## Promotion Boundary

Promote:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
```

Do not promote:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_524288
grouped_reduction_count_repeat100_262144
grouped_reduction_count_repeat100_524288
```

Keep false:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
whole_app_speedup_claim_authorized: false
```

Allow only:

```text
row_scoped_public_speedup_claim_authorized: true
```

## Goal-Level Decision Audit

Decision: record Claude/Codex consensus and promote one exact grouped_sum row.

1. Was I foolish?

   No. The decision follows Claude's approval and closes the two P0 conditions
   before promotion.

2. If yes, what actions made the decision foolish?

   It would be foolish to convert this into a V3 release, a broad V3/V2 claim,
   a whole-database claim, or promotion of the weaker excluded rows.

3. Was there another path?

   Yes. Leave the row blocked despite external approval. That would fail to
   advance Phoenix V3 toward a real user-responsible release surface.

4. Can I now try a different path that actually solves the problem?

   Yes. Promote one exact reusable row and then continue Phoenix V3 with the
   next candidate under the same review discipline.
