# Phoenix V3 RTNN Prepared Repeat50 Review Gate

Status: `rtnn_prepared_repeat50_m7_qualified_row_scoped`

This packet classifies one RTNN evidence row as a V3 `ranked_summary`
prepared-session amortization result. It is not V3 release authorization
and not a whole RTNN, one-shot, paper-equivalent, or broad V3-over-V2 claim.

## Verdict

- External review: `claude_approve_with_conditions`
- 2-AI consensus: `claude_codex_consensus_complete_approve_one_row_scoped_m7`
- M7 rows added: `1`
- Release authorized: `false`
- Broad V3-over-V2 claim authorized: `false`

## Candidate Row

- Row id: `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`
- Capability: `ranked_summary`
- Scope: `prepared repeat50 session amortization only`
- Hardware: `NVIDIA RTX 4000 Ada Generation`
- Point count / repeat / k / radius: `1048576` / `50` / `50` / `0.02`
- Hot-query speedup: `7.889x`
- Cold-plus-query speedup: `1.315x`
- Runner-wall speedup: `3.761x`
- Precision/baseline disclosure: RTDL OptiX float32 internal precision versus CuPy uniform-grid CUDA-core using float64 coordinate columns.
- Parity: integer signatures match; sum-distance relative error `1.207e-10`.
- Provenance: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/source_manifest.sha256`; no git head was available.

## Approved Row-Scoped Wording

On a single NVIDIA RTX 4000 Ada Generation GPU, RTDL OptiX ranked-summary (float32 internal precision, CUBIN cache) achieved 7.889x hot-query speedup, 1.315x cold-plus-query speedup, and 3.761x runner-wall speedup over a CuPy uniform-grid CUDA-core reference using float64 coordinate columns, at 1,048,576 points with k=50 and radius=0.02, across 50 prepared repeated queries on the same search structure. Parity was confirmed by matching integer signatures and 1.207e-10 sum-distance relative error. Source provenance is verified by source_manifest.sha256; no git head was available from the run environment. This is a scoped prepared repeated-session amortization result only.

## Accepted Conditions

- repeat50 scope disclosed in every speedup sentence
- hot-query, cold-plus-query, and runner-wall numbers travel together
- float32 OptiX versus float64-coordinate CuPy uniform-grid CUDA-core disclosed
- source_manifest.sha256 cited because no git head was available
- CuPy uniform-grid CUDA-core baseline named exactly

## Forbidden Wording

- RTNN is solved
- V3 solves nearest-neighbor search
- RTDL beats the RTNN paper implementation
- one-shot RTNN speedup
- cold-start RTNN speedup beyond the disclosed 1.315x cold-plus-query row
- 7.889x or 3.761x without the 1.315x cold-plus-query figure and repeat50 scope
- general nearest-neighbor baseline
- broad V3-over-V2 speedup
- V3 release authorization

## Review Records

- candidate_evidence: `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.json`
- repeat50_summary: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/repeat50_compare/summary.json`
- optix_payload: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/repeat50_compare/rtnn_full_batch_float32_optix.json`
- cupy_grid_payload: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/repeat50_compare/rtnn_full_batch_float32_cupy_grid.json`
- source_manifest: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/source_manifest.sha256`
- call_for_review: `docs/reviews/call_for_review_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md`
- claude_external_review: `docs/reviews/claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.md`
- claude_external_review_stream: `docs/reviews/claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.stream.jsonl`
- codex_consensus: `docs/reviews/codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md`

## Checks

- `evidence_exists`: `true`
- `evidence_status_pending_review`: `true`
- `candidate_row_id_exact`: `true`
- `release_flags_false`: `true`
- `parameters_repeat50_serious_scale`: `true`
- `hardware_gate_rtx_ada`: `true`
- `hot_and_runner_wall_material_repeat50`: `true`
- `cold_plus_query_disclosed_below_material_floor`: `true`
- `summary_comparisons_match_evidence`: `true`
- `parity_integer_signature_and_tolerance`: `true`
- `float32_float64_contract_asymmetry_disclosed`: `true`
- `source_manifest_sha256_present_no_git_head`: `true`
- `call_for_review_exists`: `true`
- `claude_external_review_approves_with_conditions`: `true`
- `claude_stream_log_exists`: `true`
- `codex_consensus_accepts_conditions`: `true`
- `approved_wording_contains_all_conditions`: `true`

Failed checks: `[]`

## Goal-Level Decision Audit

Decision: Promote exactly one RTNN prepared repeat50 ranked-summary row after Claude review and Codex consensus, with every wording/provenance condition enforced.

1. Was I foolish? No. This only accepts the reviewed prepared-session row and keeps all broader RTNN, V3-over-V2, and release claims false.
2. If yes, what actions made the decision foolish? It would be foolish to present 7.889x or 3.761x without the 1.315x cold-plus-query limitation, hide the float32/float64 baseline asymmetry, or call the CuPy grid reference a general nearest-neighbor baseline.
3. Was there another path? Leave the row pending and move to Spatial. That would avoid risk but would fail to classify a now-reviewed material prepared-session engine result.
4. Can I now try a different path? Use this gate as the only source of truth for RTNN repeat50 M7 counting, then update classification, queue, docs, and release readiness without changing the release-blocked state.
