# Goal3484 - Overlay-Area Bounded Tiled Scalar Evaluator

## Status

Implemented locally.

Goal3484 hardens the Goal3483 prepared-payload prototype with a bounded
triangle-pair tile evaluator. This is still a CPU evaluator, not a runtime GPU
kernel, but it mirrors the scratch policy from Goal3482:

- process triangle pairs through bounded triangle-pair tiles;
- accumulate row-aligned scalar area;
- report completion without silent truncation;
- fail closed when scratch capacity is invalid.

## What Changed

Updated module:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`

Added:

- `PreparedOverlayAreaTiledEvaluationResult`
- `evaluate_prepared_overlay_area_scalar_tiled(...)`

The tiled evaluator consumes the same prepared simple polygon component payload
and row-pair metadata from Goal3483. It streams triangle pairs without
materializing the full pair table, accumulates each row's scalar exact area, and
records:

- `tile_count`;
- `max_triangle_pairs_per_tile`;
- `max_observed_tile_pairs`;
- `completed_without_truncation`;
- total processed `triangle_pair_count`.

Invalid tile capacity raises an error containing:

- `scratch capacity must fail closed`

## Fixture Evidence

The validation fixture is the same concave L-shape vs square case used by
Goal3481 and Goal3483:

- left triangles: `4`;
- right triangles: `2`;
- triangle pairs: `8`;
- scalar exact area: `1.75`.

With `max_triangle_pairs_per_tile=3`, the tiled evaluator uses:

- tile count: `3`;
- max observed tile pairs: `3`;
- completed without truncation: `true`.

With `max_triangle_pairs_per_tile=1`, it streams one triangle pair per tile and
still computes the same total area.

## Boundary

This goal does not authorize a runtime kernel, public speedup wording, RT-core
speedup wording, true-zero-copy wording, release packaging, hidden dispatch,
automatic partner selection, paper reproduction claims, full overlay completion
claims, or app-specific native engine behavior.

The purpose is to make the future device continuation mechanically testable:
the device implementation should match this bounded/tiled contract rather than
inventing a different scratch behavior.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3484_overlay_area_tiled_scalar_evaluator_test`
- `py -3 -m unittest tests.goal3483_overlay_area_prepared_payload_test`
- `py -3 -m unittest tests.goal3482_overlay_area_pre_kernel_policy_test`

