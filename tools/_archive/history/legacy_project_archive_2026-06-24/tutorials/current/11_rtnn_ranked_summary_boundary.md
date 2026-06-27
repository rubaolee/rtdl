# RTNN Ranked-Summary Boundary

Status: V3 rebuild tutorial, not a release claim.

This lesson shows the RTNN boundary: the old 65,536-point materialized
ranked-summary rows are not V3 performance claims, while one newer
1,048,576-point prepared repeat50 session row is M7-qualified only under a
very narrow amortized contract.

## What This Example Teaches

RTNN is represented here as a `ranked_summary` contract: fixed-radius 3-D
neighbors with a bounded `k_max=50` summary.

The useful V3 lesson is not "RTNN is solved." The lesson is how to separate hot
query metrics, cold-plus-query timing, and prepared repeated-session wall time.

## Boundary Rows

| Distribution | Hot OptiX / Embree | Wall OptiX / Embree | Wall-time reading |
| --- | ---: | ---: | --- |
| clustered | 3.333x | 0.625x | OptiX takes about 1.60x as long as Embree |
| shell | 1.182x | 0.316x | OptiX takes about 3.16x as long as Embree |
| uniform | 1.084x | 0.303x | OptiX takes about 3.30x as long as Embree |

Wall ratios below 1.0 mean OptiX is slower than Embree. OptiX wins the hot
ranked-summary metric but loses wall timing on all three distributions. The
isolated query slice can win while initialization, orchestration, and
materialized summary-row overhead dominate the wall-time measurement at this
scale.

## M7 Prepared-Session Row

One exact RTNN harness row is now M7-qualified as `ranked_summary` evidence:

- `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`

On a single NVIDIA RTX 4000 Ada Generation GPU, RTDL OptiX ranked-summary
(float32 internal precision, CUBIN cache) achieved `7.889x` hot-query speedup,
`1.315x` cold-plus-query speedup, and `3.761x` runner-wall speedup over a CuPy
uniform-grid CUDA-core reference using float64 coordinate columns, at 1,048,576
points with `k=50` and `radius=0.02`, across 50 prepared repeated queries on
the same search structure. Parity was confirmed by matching integer signatures
and `1.207e-10` sum-distance relative error. Source provenance is
`source_manifest.sha256`; no git head was available from the run environment.

## What To Learn

- Treat clustered data as a real hot-path signal, not as universal RTNN
  acceleration.
- Treat shell and uniform as small-margin hot rows.
- Keep wall-time regression visible before any M7 discussion.
- For the M7 row, keep the repeat50 prepared-session scope and all three timing
  numbers together.
- Do not hide that summary rows are materialized and no author/external ANN
  baseline is attached.
- Do not treat these materialized summary rows as an in-device or zero-copy
  baseline.
- Do not compare this row to RTNN paper-equivalent claims.

## Source Packets

- `docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json`
- `docs/reviews/codex_phoenix_v3_rtnn_ranked_summary_intake_2ai_consensus_2026-06-20.md`
- `docs/reviews/claude_phoenix_v3_rtnn_ranked_summary_wall_time_boundary_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md`

## Claim Boundary

Allowed:

```text
RTNN ranked-summary is a V3 rebuild lesson with a distribution-specific hot
metric signal and a wall-time blocker. One separate 1,048,576-point row is
M7-qualified only as prepared repeat50 session amortization over a CuPy
uniform-grid CUDA-core reference.
```

Forbidden:

```text
Do not claim RTNN V3 is 3.333x faster.
Do not claim V3 proves universal RTNN acceleration.
Do not claim RTDL beats Embree for RTNN end to end.
Do not claim whole RTNN is M7-qualified.
Do not quote 7.889x or 3.761x without 1.315x and the repeat50 session scope.
Do not claim one-shot RTNN, cold-start RTNN, paper-equivalent RTNN, or general
nearest-neighbor acceleration.
Do not claim ranked_summary is a paper-equivalent RTNN row.
```
