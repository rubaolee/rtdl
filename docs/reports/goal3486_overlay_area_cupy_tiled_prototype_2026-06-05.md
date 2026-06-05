# Goal3486 - Overlay-Area CuPy Tiled Prototype

## Status

Implemented and pod-validated on an RTX A5000.

Goal3486 adds the first GPU execution prototype for the v2.8 scalar exact
overlay-area continuation. It consumes the Goal3483 `prepared simple polygon component payload`
and follows the Goal3484 bounded triangle-pair tile shape.

## What Changed

Updated module:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`

Added:

- `V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_CUPY_VERSION`
- `PreparedOverlayAreaCupyTiledResult`
- `evaluate_prepared_overlay_area_scalar_tiled_cupy(...)`

The CuPy RawKernel launches one thread per prepared pair row. For each row, it:

- reads left/right triangle ranges from the prepared payload;
- clips triangle pairs using a small convex triangle-triangle clipping routine;
- accumulates row-aligned float64 scalar area;
- records processed triangle-pair count;
- records tile count under `max_triangle_pairs_per_tile`;
- reports per-row status.

Status codes:

- `0`: computed;
- `1`: invalid triangle range;
- `2`: invalid tile capacity.

## Fixture Target

The local/pod fixture is the same concave L-shape vs square fixture used in
Goals3481-3484:

- left triangles: `4`;
- right triangles: `2`;
- triangle pairs: `8`;
- expected scalar area: `1.75`;
- expected tile count with `max_triangle_pairs_per_tile=3`: `3`.

## Pod Evidence

Artifact:

- `docs/reports/goal3486_overlay_area_cupy_tiled_prototype_pod_2026-06-05.json`

Pod validation:

- GPU: `NVIDIA RTX A5000`;
- CuPy: `14.1.1`;
- source commit: `fb5266bc632396693f8f8dada9873791eb7a9431`;
- row status: `[0]`;
- processed triangle pairs: `[8]`;
- tile counts: `[3]`;
- CPU total area: `1.75`;
- GPU total area: `1.75`;
- absolute error versus CPU: `0.0`;
- `completed_without_truncation`: `true`.

## Boundary

This is a CuPy RawKernel prototype over a prepared simple polygon component
payload. It is not the final native runtime path, not RT-core evidence, not a
device-resident relation-stream integration, and not a public performance
claim.

It processes bounded triangle-pair tiles and records tile counts rather than
silently truncating triangle-pair work.

This goal does not authorize release packaging, public speedup wording, RT-core
speedup wording, true-zero-copy wording, paper reproduction claims, hidden
dispatch, automatic partner selection, full overlay completion claims, or
app-specific native engine behavior.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3486_overlay_area_cupy_tiled_prototype_test`
- `py -3 -m unittest tests.goal3484_overlay_area_tiled_scalar_evaluator_test`

The CuPy test skips when CUDA/CuPy is unavailable locally, but it was executed
on the RTX A5000 pod and recorded in the artifact above.
