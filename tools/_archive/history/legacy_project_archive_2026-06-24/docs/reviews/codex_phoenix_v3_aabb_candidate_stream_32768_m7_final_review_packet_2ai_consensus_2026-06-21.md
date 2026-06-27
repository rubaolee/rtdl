# Codex 2-AI Consensus: Phoenix V3 AABB Candidate-Stream 32768 M7 Final Review Packet

Status: Claude/Codex consensus complete for one row-scoped M7-qualified result.

## Sources

```text
docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json
docs/reviews/claude_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_review_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768_float32.json
docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768.json
```

## Verdict

Codex agrees with Claude's review after applying the required P0 wording fix:
promote only this exact row to M7-qualified row-scoped status:

```text
row_id: aabb_candidate_stream_all_count_only_float32_32768
generic_capability: aabb_candidate_stream
primitive_contract: generic_prepared_aabb_index_query_2d
numeric_contract: native_float32_inclusive_boundary
boxes: 32,768
point queries: 32,768
box queries: 32,768
warmup: 2
repeat: 5
query OptiX/Embree: 814.339x
wall OptiX/Embree: 132.753x
elapsed OptiX/Embree: 73.826x
```

This consensus does not authorize a V3 release, a LibRTS paper reproduction,
LibRTS authors-code timing, full spatial-index acceleration, float64
exact-geometry wording, a V3-over-V2 speedup claim, or any other AABB row.

## Claude Findings

Claude's verdict was:

```text
CONDITIONAL APPROVE — one P0 wording change required before promotion.
```

Claude verified arithmetic, backend count parity, float32 CPU-oracle parity,
float64 mismatch disclosure, non-paper scope, non-authors-code scope,
count-only scope, and non-V2 scope.

Claude P0 condition:

```text
Embed the numeric contract directly in the 814.339x sentence:
"measured float32-inclusive query median"
```

## Codex Resolution

The P0 wording fix is applied in both the Markdown packet and JSON public
wording. The wording gate now requires this exact phrase:

```text
measured float32-inclusive query median
```

Claude's P1 tutorial note is also applied: the tutorial explains that the raw
artifact uses `operation: all`, while the review row uses `all_count_only` to
name what the route returns.

The required 2-AI chain is:

```text
Claude external review + Codex consensus
```

## Promotion Boundary

Promote:

```text
aabb_candidate_stream_all_count_only_float32_32768
```

Do not promote:

```text
contact_manifold / generic_aabb_broadphase_collect_k
any small synthetic AABB route-health row
full spatial-index acceleration
LibRTS paper/authors-code claims
float64 exact-geometry claims
V3-over-V2 claims
```

Keep false:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
librts_authors_code_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Allow only:

```text
row_scoped_public_speedup_claim_authorized: true
```

## Goal-Level Decision Audit

Decision: record Claude/Codex consensus and promote one exact AABB count-only
row.

1. Was I foolish?

   No. The decision follows Claude's conditional approval only after the P0
   wording fix is applied and guarded.

2. If yes, what actions made the decision foolish?

   It would be foolish to publish the 814.339x number without the float32
   contract, or to turn this row into a V3 release, LibRTS, full spatial-index,
   float64, or V3-over-V2 claim.

3. Was there another path?

   Yes. Leave the row blocked despite a matching float32 oracle and external
   approval. That would waste a reusable V3 capability that has now cleared the
   evidence gate.

4. Can I now try a different path that actually solves the problem?

   Yes. Promote one exact reusable AABB row, keep broad claims false, and keep
   Phoenix moving capability by capability.
