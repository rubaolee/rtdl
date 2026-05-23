# Goal2564: Active Engine App-Independence Boundary

Date: 2026-05-23

## Scope

This closeout records the app-independence boundary after the v2.x benchmark
cleanup wave. The claim is intentionally narrow: active native Embree/OptiX
engine paths and shared partner/columnar modules should not carry benchmark-app
vocabulary or app-specific adapter implementations.

The scope does not claim that every compatibility wrapper has been renamed, and
it does not reopen inactive backend work.

## Current State

- The active native Embree/OptiX engine paths are the checked native boundary
  for this cleanup.
- Active native Embree/OptiX engine paths are app-name-free for the supported
  primitive work covered by this cleanup.
- `src/rtdsl/partner_adapters.py` no longer contains the robot-collision pose
  adapter or the Barnes-Hut pairwise inverse-square force adapter.
- Shared columnar wording no longer describes the contract as RayDB-specific.
- Python app adapters now own app-specific compositions under
  `src/rtdsl/app_adapters/`.

## Explicit Non-Claims

- Python compatibility wrappers still contain legacy DB-shaped names for
  compatibility and app-facing routing. That is acceptable under the current
  boundary because Python remains the app-specific control/lowering layer.
- Legacy native compatibility/proof surfaces outside active Embree/OptiX
  cleanup are not promoted by this report.
- Vulkan/HIPRT/Apple RT are explicitly out of scope before v2.1.
- This is not a universal-compute-engine claim. It is an app-knowledge boundary
  claim for RTDL's active ray-tracing primitive engine paths.

## Validation

Added `Goal2564ActiveEngineAppIndependenceBoundaryTest`, which scans:

- `src/native/embree`
- `src/native/optix`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/columnar_partner.py`

The test rejects app/domain vocabulary such as DBSCAN, RayDB, robot collision,
Barnes-Hut, and pairwise inverse-square force names in those active/shared
surfaces.

No pod was used. This is local boundary documentation and automated regression
coverage.
