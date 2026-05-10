# Goal1660 Measured Pod Summary 3-AI Consensus

## Verdict

`measured_evidence_accepted_release_blocked`

Codex, Claude, and Gemini agree that the Goal1660 pod evidence is valid for the rows that actually ran, and that v1.6.11 must remain blocked from release/public speedup claims based on this package.

## Consensus Points

- The reported count is honest: `16` accepted measured app/engine pairs and `20` unsupported, excluded, or shared-alias pairs across `36` total public app/engine slots.
- The `--backend` versus `--mode` correction is required. `--backend` is a real Embree/OptiX selector in this benchmark package; `--mode` is often an execution-mode flag such as `run`, `dry-run`, or `optix`, so rewriting it to `embree` creates fake rows.
- The corrected OptiX reruns for `--mode run` scripts are accepted measured rows, not speculative fixes.
- Embree coverage is currently missing for most release-facing app profilers. That is an app-profiler/product-surface gap, not an RTX pod failure.
- The data does not support a public v1.6.11 speedup claim. Several accepted OptiX rows are slower than v1.0, and the largest measured ratio in this package is `1.138` for `segment_polygon_anyhit_rows/optix`.
- Release, tag, and public speedup claims remain blocked.

## Review Inputs

- Codex pod execution: `docs/reports/goal1660_pod_execution_raw_2026-05-10.json`
- Codex corrected OptiX reruns: `docs/reports/goal1660_pod_corrected_optix_rows_2026-05-10.json`
- Codex measured summary: `docs/reports/goal1660_v1_6_11_vs_v1_0_pod_summary_2026-05-10.md`
- Claude review: `docs/reviews/goal1660_measured_pod_summary_claude_review_2026-05-10.md`
- Gemini review: `docs/reviews/goal1660_measured_pod_summary_gemini_review_2026-05-10.md`

## Next Fixes

Before v1.6.11 can be treated as a performance release candidate, RTDL needs either accepted performance parity/speedup evidence or a narrowed non-performance release scope. Separately, release-facing app profilers need standard `--backend` coverage if Embree-vs-OptiX app comparisons are required for every app.
