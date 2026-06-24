# Call For Review: Phoenix V3 RTNN Full-Batch Float32 Same-Contract RTX Evidence

Date: 2026-06-21

Please critically review the Phoenix V3 RTNN evidence packet:

- Evidence packet: `docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md`
- Machine packet: `docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.json`
- Main raw evidence: `docs/rebuild/v3/evidence/rtnn_full_batch_float32_same_contract_1048576_r5_20260621/summary.json`
- Runner: `scripts/v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py`
- Queue: `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`

## Current Codex Classification

Codex classifies this as:

`rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7`

The main 1,048,576-point repeat5 RTX run has same-contract parity against the
CuPy grid reference. Prepared RTDL OptiX hot query is 7.790x faster than the
same-contract CuPy grid reference, but cold-plus-query wall speedup is 0.393x
and runner-wall speedup is 0.627x because load, pack, and OptiX preparation
dominate.

All release flags are false. M7 rows added by the packet: 0.

## Review Questions

1. Is the packet technically honest and internally consistent?
2. Is the current classification correct: a prepared-hot-query candidate pending
   external review, while still not M7 and blocked for wall/end-to-end wording?
3. Should this evidence ever be eligible for an M7 row if the public row is
   explicitly scoped to prepared hot-query only, or should the wall regression
   block any M7 promotion?
4. Are the not-M7 blockers complete?
5. Are the forbidden shortcuts strong enough to prevent misleading user-facing
   RTNN, V3-over-V2, paper, or universal nearest-neighbor claims?
6. What concrete engine work should happen next: pack/prepare amortization,
   exact/tie-stable repair, a different reference, or no further RTNN promotion
   work?

Please return a direct verdict:

- `approve_as_hot_query_candidate_not_m7`
- `approve_with_required_fixes`
- `reject_candidate_keep_not_m7`

Also list required fixes before any future M7 promotion.
