# RTDL v0.9.6 Release Package

Status: released as `v0.9.6`.

`v0.9.6` is the prepared/prepacked visibility-count optimization release. It
packages the post-`v0.9.5` work from Goals650-684.

## Scope

This release records the surface after `v0.9.5`:

- Vulkan native early-exit any-hit is available after rebuilding the current
  Vulkan backend library.
- Apple RT has 3D MPS RT any-hit and 2D MPS-prism
  native-assisted any-hit after rebuilding the Apple RT backend library.
- Apple RT has a prepared/prepacked scalar 2D visibility-count app path.
- OptiX has prepared/prepacked 2D any-hit count paths for repeated visibility
  queries.
- HIPRT has prepared 2D any-hit reuse on the HIPRT/Orochi CUDA path.
- Vulkan has prepared 2D any-hit with packed-ray support.
- Public docs, history indexes, local release gates, and Linux backend gates
  have been refreshed through Goal684.

## Boundary

Allowed conclusion:

> RTDL `v0.9.6` has a validated prepared/prepacked repeated 2D
> visibility/count optimization line across Apple RT, OptiX, HIPRT, and Vulkan,
> with backend-specific contracts and honesty boundaries.

Disallowed conclusions:

- broad DB, graph, full-row, or one-shot speedup;
- RT-core speedup from the GTX 1070 Linux host;
- AMD GPU validation for HIPRT;
- Apple RT full emitted-row speedup from the scalar count path;
- Apple MPS ray-tracing traversal for DB or graph workloads;
- a broad speedup claim outside the documented prepared/prepacked
  visibility/count contracts.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Record](tag_preparation.md)
- [Current Main Support Matrix](../../current_main_support_matrix.md)
- [Goal676/677 Closure And Doc Refresh](../../reports/goal676_677_cross_engine_optimization_closure_and_doc_refresh_2026-04-20.md)
- [Goal678 Local Total Gate](../../reports/goal678_local_total_test_doc_flow_audit_2026-04-20.md)
- [Goal679 Linux Backend Gate](../../reports/goal679_linux_gpu_backend_release_gate_2026-04-20.md)
- [Goal680 History Catch-Up Consensus](../../reports/goal680_consensus_2026-04-20.md)
- [Goal681 Post-History Release Gate Consensus](../../reports/goal681_consensus_2026-04-20.md)
- [Goal683 Final Local Gate Consensus](../../reports/goal683_consensus_2026-04-21.md)
- [Goal684 Release-Level Flow Audit](../../reports/goal684_v0_9_6_release_level_flow_audit_2026-04-21.md)

## Latest Gate Evidence

- local full discovery after release packaging: `1274` tests OK, `187` skips
- public command truth audit: valid, `250` commands across `14` docs
- public entry smoke: valid
- focused public release-doc tests: `20` tests OK
- focused history regression: `4` tests OK
- Linux fresh backend gate: OptiX, Vulkan, and HIPRT build and focused native
  tests pass on the GTX 1070 host
- Codex, Claude, and Gemini Flash accepted Goals681-684

## Release State

This package is the released `v0.9.6` public boundary after maintainer
authorization, release-level flow audit, and final local gate evidence.
