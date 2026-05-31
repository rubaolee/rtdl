# Goal2801 Hausdorff/X-HD v2.5 Canonical Entrypoint Consensus

Date: 2026-05-31

Consensus status: accept-with-boundary.

AI reviewers:

- Codex: implemented the canonical exact Hausdorff/X-HD entrypoint, manifest update, first pod artifact, and report.
- Claude: independent external review saved at `docs/reviews/goal2801_claude_review_hausdorff_xhd_canonical_entrypoint_2026-05-31.md`, verdict `accept-with-boundary`.

## Consensus

Goal2801 is accepted with boundary:

- the `hausdorff_xhd` v2.5 row now has a canonical exact entrypoint instead of scattered method notes;
- the entrypoint compares exact `cupy_grouped_grid_rawkernel` with exact `rtdl_rt_grouped_adaptive_nearest_witness`;
- the first pod artifact records exact scalar and witness agreement between the CuPy grid opponent and the RTDL/OptiX path;
- the RTDL/OptiX path is correctly recorded as RT-core accelerated;
- the report honestly records that the RTDL/OptiX path is much slower than the CuPy grid opponent on the 4K fixture;
- public speedup, whole-app speedup, RTDL-beats-X-HD, RTDL-beats-CuPy-grid, broad RT-core speedup, Triton speedup, full paper reproduction, and native app-customization claims remain unauthorized.

## Clean-From-Git Validation

The first evidence artifact was produced on the pod with the Goal2801 script copied into an existing checkout before the Goal2801 commit was pushed. That boundary is now closed by a clean-from-Git pod rerun.

Clean-from-Git validation:

- commit: `7a764ad8b742fb621c0fcc0154335f5b19c251f1`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- OptiX build: pass
- Goal2801 harness: pass
- distance error vs CuPy grid: 0.0
- RTDL method uses RT cores: true
- RTDL/CuPy elapsed ratio: 144.04x slower
- focused pod test slice: 20 tests run, 20 passed

## Boundary

This consensus does not authorize a public speedup claim. The accepted claim is narrower: the canonical entrypoint exists, the same-contract comparison is exact, the first pod artifact is internally consistent, and the claim boundary is preserved.
