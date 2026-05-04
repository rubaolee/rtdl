# RTDL v1.0 Release Package

Status: released as `v1.0`.

The current released version is `v1.0`.

`v1.0` is the app-shaped RTDL proof release. It packages the current
main documentation, examples, app inventory, and bounded performance evidence
showing that a Python-facing ray-tracing DSL can express useful non-rendering
workloads across real backend surfaces. It is not the final performance
architecture.

## Scope

This release package records the `v1.0` boundary:

- a compact public front page and documentation router for new users;
- tutorials and app/example docs for the Python-hosted RTDL authoring path;
- architecture, programming-model, IR/lowering, and performance docs that
  describe the current user contract;
- `18` app rows in the v1.0 acceleration inventory;
- `12` reviewed bounded NVIDIA RTX public wording rows;
- continued blocking or non-review status for app rows without reviewed
  same-contract public speedup wording;
- selected Vulkan, HIPRT, and Apple RT proof surfaces without making them new
  v1.0 performance-release targets;
- explicit acceptance that v1.0 still contains app-specific native
  continuations where needed.

## Boundary

Allowed conclusion:

> RTDL `v1.0` is the foundation proof that a Python-facing RT DSL can express
> real app-shaped traversal workloads and connect them to audited backend
> surfaces with bounded, reviewed performance wording.

Disallowed conclusions:

- a broad whole-app speedup claim;
- a broad all-app NVIDIA RT-core speedup claim;
- a claim that all `--backend optix` runs prove RT-core speedup;
- a claim that Vulkan, HIPRT, or Apple RT have new v1.0 public speedup
  promotions;
- a claim that app-specific native continuations are already removed;
- a claim that v1.0 is the v2.0 end-to-end performance architecture.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [v1.0 App Acceleration Inventory](../../v1_0_app_acceleration_inventory.md)
- [v1.0 RTX App Status](../../v1_0_rtx_app_status.md)
- [Performance Model](../../performance_model.md)
- [Current Architecture](../../current_architecture.md)
- [IR And Lowering](../../rtdl/ir_and_lowering.md)

## Release Gate State

- Implementation and bounded evidence are complete for the released v1.0 proof
  boundary.
- Recent public-doc focused gates passed after front-page and tutorial polish.
- No immediate pod is required unless the release scope changes to promote a
  blocked or not-reviewed app row into new public speedup wording.
- Full local discovery, external-AI review, final authorization, and version
  marker update completed before the release action.

## Release State

This package is the released `v1.0` boundary. It must still not be cited as a
whole-app speedup authorization or as new public wording for blocked or
not-reviewed rows.
