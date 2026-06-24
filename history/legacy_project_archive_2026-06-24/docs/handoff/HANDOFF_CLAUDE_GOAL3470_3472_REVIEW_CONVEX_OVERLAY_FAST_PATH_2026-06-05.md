# Handoff: Claude Review Of Goal3470-3472 Convex Overlay Fast Path

## Task

Please perform an independent read-only review of the Goal3470-3472 Spatial
RayJoin overlay-area work and write the review to:

`docs/reviews/goal3473_claude_review_convex_overlay_fast_path_3470_3472_2026-06-05.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Scope To Review

- `src/rtdsl/geometry_relation_continuations.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `scripts/goal3471_convex_overlay_area_fast_path_probe.py`
- `tests/goal3470_simple_polygon_overlay_area_continuation_design_test.py`
- `tests/goal3471_convex_overlay_area_fast_path_probe_test.py`
- `tests/goal3472_v2_8_runtime_gap_after_convex_overlay_fast_path_test.py`
- `docs/reports/goal3470_simple_polygon_overlay_area_continuation_design_2026-06-05.md`
- `docs/reports/goal3471_convex_overlay_area_fast_path_probe_2026-06-05.md`
- `docs/reports/goal3471_convex_overlay_area_fast_path_probe_pod_2026-06-05.json`
- `docs/reports/goal3472_v2_8_runtime_gap_after_convex_overlay_fast_path_2026-06-05.md`
- `docs/research/future_version_to_do_list.md`

Context:

- `docs/reports/goal3467_shape_pair_relation_complexity_probe_2026-06-05.md`
- `docs/reports/goal3468_v2_8_runtime_gap_after_relation_complexity_2026-06-05.md`
- `docs/reviews/goal3469_gemini_review_rayjoin_relation_complexity_gap_3467_3468_2026-06-05.md`

## Review Questions

1. Does Goal3470 correctly conclude that public-CDB exact overlay needs a
   generic simple-polygon overlay-area continuation rather than a convex-only
   shortcut?
2. Does Goal3471 implement a generic convex overlay-area continuation over the
   existing relation-stream contract, without RayJoin/app-specific native logic?
3. Does the synthetic fixture in the Goal3471 pod artifact validate the convex
   fast-path area computation (`1.0` expected and measured)?
4. Does the public-CDB evidence correctly show this fast path is bounded to 168
   supported rows and 4,375 unsupported nonconvex rows?
5. Does Goal3472 update the runtime gap map honestly, preserving the full
   nonconvex/general overlay gap?
6. Are all release, speedup, RT-core, true-zero-copy, RayJoin reproduction,
   RTDL-beats-RayJoin, and full-overlay-completion claims still blocked?

## Boundaries

- This is a read-only review. Do not edit source files.
- Only write the requested review file under `docs/reviews/`.
- Do not authorize release or any public performance claim.
- If the convex fast path is sound but full nonconvex overlay remains open,
  prefer `accept-with-boundary`.

