# Goal1660 v1.6.11 vs v1.0 Performance Matrix 3-AI Consensus

## Verdict

`ready_for_pod_execution_not_release`

Codex, Claude, and Gemini agree that the Goal1660 preparation package is ready for NVIDIA RT pod execution. It is not a release, tag, or public speedup-claim authorization.

## Consensus Points

- The matrix covers every public app with Embree and OptiX row slots, but only counts rows as comparable when the command can genuinely select that engine or is explicitly OptiX-specific.
- The graph Embree row is correctly excluded because the source command has no engine selector; the graph OptiX row remains planned through the OptiX-specific script.
- The DBSCAN OptiX row is correctly marked as `shared_primitive_alias` to `outlier_detection`, so it provides app coverage but is not counted as an independent cross-version timing row.
- The blocked-claim set correctly includes whole-app speedup, broad RTX/GPU acceleration, true zero-copy, stable collect-k bounded promotion, Python+partner+RTDL, and v1.6.11 release/tag action.
- The pod contract correctly requires two clean checkouts, separate per-engine builds, provenance recording, strict parity/status acceptance, and unsupported classification for missing v1.0 scripts or schema drift.

## Review Inputs

- Codex local validation: `py -3 -m unittest tests.goal1660_v1_6_11_vs_v1_0_perf_matrix_test tests.goal1659_v1_6_11_perf_matrix_test` passed with 12 tests when run with `PYTHONPATH=src;.`.
- Claude review: `docs/reviews/goal1660_v1_6_11_vs_v1_0_perf_matrix_claude_review_2026-05-10.md`
- Gemini review: `docs/reviews/goal1660_v1_6_11_vs_v1_0_perf_matrix_gemini_review_2026-05-10.md`

## Boundary

The next valid step is pod execution of the accepted rows. The package must not be used to publish v1.6.11 or claim public speedups until measured artifacts pass the pod contract and are reviewed.
