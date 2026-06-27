# Phoenix V3 AABB Prepare-Reuse Contract

Status: `aabb_prepare_reuse_contract_candidate_not_m7`.

This packet advances the AABB queue item by making the reusable
`aabb_index_query_2d` prepared-session contract visible in the contact
broadphase harness. It does not promote a new M7 row.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Existing AABB M7 Row

- Row: `aabb_candidate_stream_all_count_only_float32_32768`
- Scope: `native_float32_inclusive_count_only_32768`
- This remains the only AABB M7 row.

## Current Contact Gap

- Row: `contact_manifold / generic_aabb_broadphase_collect_k`
- Query OptiX/Embree: `1.235x`
- Collect-k OptiX/Embree: `2.759x`
- Prepare AABB-index OptiX/Embree: `0.243x`
- Wall OptiX/Embree: `0.803x`

Hot query and bounded-row collection improve, but OptiX AABB-index preparation dominates enough that the current wall path is slower.

## Runtime Contract Smoke

- Primitive: `aabb_index_query_2d`
- Contract version: `rtdl.v2_10.prepared_session_residency.goal3873.v1`
- Cold phase: `prepare_aabb_index_2d`
- Hot phase: `emit_aabb_intersection_pair_rows_2d`
- Explicit reuse helper: `get_or_prepare_explicit_session`
- Public speedup, device-buffer interop, automatic partner selection, and app-specific native logic remain false.
- This packet records contract visibility. It does not claim the current local smoke observed a prepared AABB execution path or a performance win.

## POD Runner

- Script: `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
- Status: `runner_available_not_yet_rt_pod_evidence`
- Serious default command:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py --dataset jittered_grid --grid-count 32768 --warmup 3 --repeat 50 --backends embree,optix --require-rt-hardware --output-dir docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_YYYYMMDD
```

- The runner alone does not authorize M7 promotion; a successful RTX run still needs fresh external review plus Codex consensus.

## Review Status

- External review: `claude_approve_with_amendments_p1_applied`
- 2-AI consensus: `claude_codex_consensus_complete_queue_advancement_not_m7`
- Claude review: `docs/reviews/claude_phoenix_v3_aabb_prepare_reuse_contract_review_2026-06-21.md`
- Codex consensus: `docs/reviews/codex_phoenix_v3_aabb_prepare_reuse_contract_2ai_consensus_2026-06-21.md`

## Future M7 Requirements

- Use the generic aabb_index_query_2d prepared-session contract, not contact-specific native logic.
- Use a serious fixture: at least 32,768 indexed AABBs and 32,768 query AABBs, or a reviewer-approved equivalent scale with a non-trivial prepare phase.
- Prepare indexed AABB scene once, then run repeated query/collect rows under an explicit user session.
- Report prepare/query/collect/wall phases separately and include cold-plus-repeat wall timing.
- Keep CPU-reference parity and fail-closed overflow behavior visible.
- Show material OptiX wall win after prepare reuse, not only hot-query win; 1.01x-style noise is not enough.
- Obtain fresh external review plus Codex consensus before any new M7 row.

## Forbidden Shortcuts

- Do not promote contact_manifold from this packet.
- Do not claim full contact solver or physics throughput.
- Do not claim device-buffer interop or automatic partner selection.
- Do not use the existing 1.235x query ratio as wall or end-to-end speedup.
- Do not claim a broad V3-over-V2 AABB/contact speedup.

## Goal-Level Decision Audit

Decision: Add generic AABB prepare-reuse contract visibility without promoting a new M7 row.

1. Was I foolish?
   No. The current contact row is wall-slower, so the honest move is to expose the reusable prepared-session contract before rerunning performance.
2. If yes, what actions made the decision foolish?
   It would be foolish to publish the 1.235x query or 2.759x collect-k ratios while ignoring the 0.803x wall ratio and 0.243x prepare ratio.
3. Was there another path that would have avoided getting stuck on that idea?
   Directly rerun the pod. That may be needed next, but without a generic prepared-session contract the rerun would not prove a V3 engine capability.
4. Can I now try a different path that actually solves the problem?
   Keep AABB in the engine queue as a prepare-reuse candidate and require a repeated-session POD row with wall win, parity, overflow behavior, and 2-AI review.
