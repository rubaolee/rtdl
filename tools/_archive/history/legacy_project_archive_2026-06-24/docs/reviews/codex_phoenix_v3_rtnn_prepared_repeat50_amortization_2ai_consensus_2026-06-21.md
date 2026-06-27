# Codex Consensus: Phoenix V3 RTNN Prepared Repeat50 Amortization

Status: `claude_codex_consensus_complete_approve_one_row_scoped_m7`

This is Codex's consensus response to Claude's external review:

- `docs/reviews/claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.md`
- `docs/reviews/call_for_review_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.md`

## Decision

Promote exactly one Phoenix V3 row-scoped M7 result:

- `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`

The promoted capability is `ranked_summary`, using RTNN only as the evidence
harness. This is not V3 release authorization and not a whole RTNN, one-shot
nearest-neighbor, paper-equivalent, or broad V3-over-V2 claim.

```text
m7_rows_added: 1
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
whole_rtnn_claim_authorized: false
one_shot_rtnn_claim_authorized: false
paper_equivalent_claim_authorized: false
```

## Conditions Accepted From Claude

Codex accepts Claude's `APPROVE_WITH_CONDITIONS` verdict and treats the following
conditions as hard M7 gate requirements:

1. Any public speedup wording must say the result is across 50 prepared repeated
   queries on the same search structure.
2. Hot-query `7.889x`, cold-plus-query `1.315x`, and runner-wall `3.761x` must
   travel together. No single number is allowed as standalone headline wording.
3. The precision and baseline must be stated as RTDL OptiX float32 internal
   precision versus CuPy uniform-grid CUDA-core using float64 coordinate
   columns. Parity is only the observed ranked-summary parity with
   `1.207e-10` sum-distance relative error.
4. Provenance must cite `source_manifest.sha256`; the pod environment had no
   git head.
5. The baseline must be named as CuPy uniform-grid CUDA-core, not "the RTNN
   baseline" or a general nearest-neighbor baseline.

## Approved Row Wording

On a single NVIDIA RTX 4000 Ada Generation GPU, RTDL OptiX ranked-summary
(float32 internal precision, CUBIN cache) achieved `7.889x` hot-query speedup,
`1.315x` cold-plus-query speedup, and `3.761x` runner-wall speedup over a CuPy
uniform-grid CUDA-core reference using float64 coordinate columns, at 1,048,576
points with `k=50` and `radius=0.02`, across 50 prepared repeated queries on
the same search structure. Parity was confirmed by matching integer signatures
and `1.207e-10` sum-distance relative error. Source provenance is verified by
`source_manifest.sha256`; no git head was available from the run environment.
This is a scoped prepared repeated-session amortization result only.

## Forbidden Wording

- Do not say RTNN is solved.
- Do not say V3 solves nearest-neighbor search.
- Do not compare this row to the RTNN paper implementation.
- Do not imply a one-shot or cold-start RTNN win.
- Do not quote `7.889x` or `3.761x` without the `1.315x` cold-plus-query figure
  and the repeat50 session scope.
- Do not imply generality to FAISS, cuML, CPU SIMD, Embree, or other nearest
  neighbor baselines.
- Do not use this row as V3 release authorization.
- Do not infer broad V3-over-V2 speedup from this row.

## Goal-Level Decision Audit

Decision: accept the Claude review and promote one exact RTNN prepared repeat50
row only after turning all wording/provenance conditions into gate checks.

1. Was I foolish? No. This decision uses the external review as a constraint,
   not as permission to generalize.
2. If yes, what actions made the decision foolish? It would be foolish to quote
   only the 7.889x hot-query or 3.761x session-wall number, omit the 1.315x
   cold-plus-query limitation, or call the row a whole RTNN or V3-over-V2 win.
3. Was there another path? Yes. I could keep RTNN pending and move to Spatial,
   but that would leave a reviewed, material prepared-session engine result
   unclassified.
4. Can I now try a different path that actually solves the problem? Yes. Add a
   dedicated RTNN review gate, count exactly this one row in the M7 packet, close
   the RTNN queue item, and keep release authorization false.
