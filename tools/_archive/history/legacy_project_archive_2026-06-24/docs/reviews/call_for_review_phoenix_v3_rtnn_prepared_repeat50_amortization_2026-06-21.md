# Call For Review: Phoenix V3 RTNN Prepared Repeat50 Amortization Candidate

Status: request for external Claude/Gemini review; not M7 promotion and not
release authorization.

Please review only this scoped candidate row:

- `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`

Primary evidence:

- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/repeat50_compare/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/repeat50_compare/rtnn_full_batch_float32_optix.json`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/repeat50_compare/rtnn_full_batch_float32_cupy_grid.json`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/source_manifest.sha256`

Question:

Can this exact row be accepted as a Phoenix V3 M7 candidate after external
review, while keeping release authorization false and keeping all broad
V3-over-V2 / whole-RTNN / one-shot RTNN wording forbidden?

Observed POD facts:

- Same hardware: NVIDIA RTX 4000 Ada Generation.
- Point count: 1,048,576.
- Repeat count: 50.
- Point source: NPZ column source on both OptiX and CuPy grid routes.
- Same-contract parity: integer signatures match; sum-distance relative error
  is `1.207e-10`.
- RTDL OptiX hot-query speedup over CuPy grid: `7.889x`.
- RTDL OptiX cold-plus-query speedup over CuPy grid: `1.315x`.
- RTDL OptiX runner-wall speedup over CuPy grid: `3.761x`.

Required boundaries:

- This is a prepared repeated-session amortization row only.
- This is not a one-shot RTNN speedup claim.
- This is not a whole-app RTNN claim.
- This is not a paper-equivalent claim.
- This is not V3 release authorization.
- This is not a broad V3-over-V2 claim.

Please answer:

1. Verdict: `APPROVE`, `APPROVE_WITH_CONDITIONS`, or `BLOCK`.
2. Critical findings, ordered P0/P1/P2, each tied to file evidence.
3. Required changes before M7, if any.
4. Allowed public wording for this exact row, if approved.
5. Any wording that must remain forbidden.
