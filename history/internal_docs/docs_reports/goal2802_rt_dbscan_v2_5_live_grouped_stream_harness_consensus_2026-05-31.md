# Goal2802 RT-DBSCAN v2.5 Live Grouped-Stream Harness Consensus

Date: 2026-05-31

Consensus status: accept-with-boundary.

AI reviewers:

- Codex: implemented the live RT-DBSCAN grouped-stream harness, manifest update, first pod artifact, and report.
- Claude: independent external review saved at `docs/reviews/goal2802_claude_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md`, verdict `accept-with-boundary`.
- Gemini: independent external review saved at `docs/reviews/goal2802_gemini_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md`, verdict `accept-with-boundary`.

## Consensus

Goal2802 is accepted with boundary:

- the `rt_dbscan` v2.5 row now has a current live harness instead of relying only on historical Goal2478 artifacts;
- the harness records the same-contract prepared CuPy grid opponent, prepared RTDL/OptiX count bridge, and RTDL/OptiX grouped-stream continuation;
- all three point counts pass signature checks;
- the grouped stream is recorded as RT-core accelerated;
- the grouped stream avoids neighbor-row materialization and avoids a full directed-adjacency stream;
- the first pod artifact records grouped-stream speedups of 4.019x, 4.883x, and 4.684x over the prepared CuPy grid opponent on the three clustered3d fixtures;
- public speedup, whole-app speedup, paper reproduction, paper-level speedup, broad DBSCAN speedup, pure Triton component, and native app-customization claims remain unauthorized;
- pure Triton component auto-selection remains blocked until a generic component continuation beats the same-contract CuPy/grid/grouped-stream opponent.

## Clean-From-Git Validation

The first evidence artifact was produced by copying the new Goal2802 harness into a pod checkout at commit `afcea27599c4738cdee62b111e22c3111598efe8`. That first-run boundary is disclosed in the report and in the artifact `source_dirty` field.

That boundary is now closed by a clean-from-Git pod rerun.

Clean-from-Git validation:

- commit: `676844e4dc9d0883984827a2b6241781167020ef`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- OptiX build: pass
- Goal2802 harness: pass, 3 rows
- signatures match: true
- grouped stream uses RT cores: true
- grouped stream avoids neighbor rows and full directed adjacency stream: true
- grouped-stream speedups vs prepared CuPy grid: 4.289x, 4.829x, 4.910x
- focused pod test slice: 16 tests run, 16 passed

## Boundary

This consensus does not authorize a paper, broad DBSCAN, whole-app, pure Triton, or public speedup claim. The accepted claim is narrower: the live harness exists, the same-contract comparison is current, the grouped-stream generic continuation is correct on the recorded fixtures, and the claim boundary is preserved.

Goal2804 later refreshed the clean artifact metadata at commit
`6ae202919c2af07ae8d8a9c662edd656ae77aa87`; the refreshed artifact remains
`pass` and records `source_dirty: []`.
