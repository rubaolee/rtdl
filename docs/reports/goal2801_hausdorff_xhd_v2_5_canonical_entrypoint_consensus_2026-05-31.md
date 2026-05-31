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

## Boundary

The current evidence artifact was produced on the pod with the Goal2801 script copied into an existing checkout before the Goal2801 commit was pushed. This is useful first evidence, but not final reproducibility evidence.

Clean-from-Git validation remains required before final evidence closure:

- fetch/reset the pod checkout to `origin/main` after the Goal2801 commit is pushed;
- rebuild `librtdl_optix.so`;
- rerun the Goal2801 entrypoint from the committed file;
- rerun the focused test slice;
- record the clean artifact and commit hash in the Goal2801 report.

This consensus does not authorize a public speedup claim. The accepted claim is narrower: the canonical entrypoint exists, the same-contract comparison is exact, the first pod artifact is internally consistent, and the claim boundary is preserved.
