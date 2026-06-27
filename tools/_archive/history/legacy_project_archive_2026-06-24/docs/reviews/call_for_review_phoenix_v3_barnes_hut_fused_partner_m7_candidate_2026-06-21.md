# Call For Review: Phoenix V3 Barnes-Hut Fused Partner M7 Candidate

Reviewer: Claude or Gemini external AI.

Please critically review this candidate packet:

- Candidate packet: `docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.json`
- Candidate markdown: `docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md`
- Same-basis no-go packet: `docs/rebuild/v3/phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.json`
- Candidate script: `scripts/v3_phoenix_barnes_hut_fused_partner_m7_candidate.py`
- Candidate test: `tests/v3_phoenix_barnes_hut_fused_partner_m7_candidate_test.py`

Context:

- Phoenix V3 must promote reusable, evidence-backed engine/language capabilities only.
- The current prepared RTDL/OptiX aggregate-frontier emission path is now explicitly no-go under one wall-time basis.
- The positive remaining path is a generic Numba CUDA partner contract:
  `generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1`.
- It is app-agnostic in source, has a small exact CPU-reference smoke, avoids frontier/contribution materialization on the hot path, and is faster than CPU/Numba fused by at least 3.102x across the large saved rerun scales.
- At 131,072 bodies, the candidate route is 45.493 ms wall-repeat median, 4.082x faster than CPU/Numba fused and 13.591x faster than the current prepared RTDL/OptiX frontier-emission route.
- This packet does not promote a row. It asks whether one row-scoped V3 partner capability can be promoted after review.

Questions:

1. Is this a legitimate V3 language/engine capability, or merely Barnes-Hut app tuning?
2. Is the evidence sufficient to promote exactly one row-scoped M7 candidate after review?
3. Are the blockers honest enough: no RT-core claim, no whole-app Barnes-Hut claim, no paper reproduction, no broad V3-over-V2 claim?
4. Does the large-row validation basis, route parity plus checksums plus small exact CPU smoke, need a fresh POD rerun before promotion?
5. If approved, what exact wording and row id should be allowed?

Required verdict format:

- `approve`
- `approve-with-amendments`
- `block`

Please be strict. If this is not enough for M7, state the missing evidence clearly.
