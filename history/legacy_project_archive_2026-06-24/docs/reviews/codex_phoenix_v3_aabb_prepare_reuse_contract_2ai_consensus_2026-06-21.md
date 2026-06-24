# Codex 2-AI Consensus: Phoenix V3 AABB Prepare-Reuse Contract

Status: `claude_codex_consensus_complete_queue_advancement_not_m7`.

## Verdict

Codex accepts the AABB prepare-reuse packet as a valid Phoenix V3 queue
advancement after Claude review and P1 amendments. It is not an M7 promotion,
not release authorization, and not public speedup wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added: 0
```

## Review Inputs

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_aabb_prepare_reuse_contract_review_2026-06-21.md`
- Packet:
  `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md`

Claude verdict: `approve_with_amendments`.

Claude found no P0 blockers. Two P1 amendments were required before the packet
could be cited in a future POD attempt:

- Add a serious fixture scale floor for future M7 evidence.
- Clarify that current metadata is contract visibility, not observed prepared
  execution or performance proof in this packet.

Both P1 amendments are applied in the regenerated packet.

## Accepted Scope

Accepted:

- The contact broadphase harness now emits generic `aabb_index_query_2d`
  prepared-session residency metadata.
- The packet keeps existing contact evidence as wall-slower on OptiX:
  `wall_optix_over_embree: 0.8029757821318222`.
- The only current AABB M7 row remains
  `aabb_candidate_stream_all_count_only_float32_32768`.
- The next AABB queue action is a serious repeated-session POD row with
  CPU-reference parity, fail-closed overflow behavior, separate
  prepare/query/collect/wall phases, and a material OptiX wall win after
  prepare reuse.

Not accepted:

- No contact-manifold M7 row.
- No full contact solver or physics throughput claim.
- No broad V3-over-V2 claim.
- No device interop or automatic partner claim.
- No public wording from the current AABB prepare-reuse packet.

## Goal-Level Decision Audit

Decision: accept the AABB prepare-reuse packet as non-M7 queue advancement after
Claude review and P1 amendments.

1. Was I foolish?
   No. The decision preserves the wall-slower contact boundary and uses Claude's
   critique to tighten future evidence requirements before any POD claim.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to treat contract metadata as observed
   performance evidence or to allow tiny fixtures to satisfy the future M7
   rerun gate.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could have skipped external review and called the packet closed from
   local tests only. That would repeat the old failure mode of trusting local
   wording too much.
4. Can I now try a different path that actually solves the problem?
   Yes. The next AABB work is a serious repeated-session POD rerun, not more
   prose: at least 32,768 indexed AABBs and 32,768 query AABBs or a
   reviewer-approved equivalent scale, with wall timing and parity evidence.
