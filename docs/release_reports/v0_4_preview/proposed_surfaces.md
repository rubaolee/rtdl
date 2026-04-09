# RTDL v0.4 Preview: Proposed Surfaces

## Headline public surface

- `point_in_volume`

## Supporting surfaces

- stronger public `ray_tri_hitcount` documentation and examples
- one bounded non-demo 3D example chain
- continued hidden-star visual demo only as proof-of-capability support

## Proposed first public user story

Users have:

- 3D points
- closed triangle meshes

They want:

- to classify which points lie inside which volumes

RTDL should provide:

- a bounded public workload for that task

## Proposed emitted fields

- `point_id`
- `volume_id`
- `contains`

## Proposed first boundary

- closed manifold meshes only
- bounded parity-style classification
- explicit limitations around degenerate or non-manifold meshes
- explicit backend support matrix
