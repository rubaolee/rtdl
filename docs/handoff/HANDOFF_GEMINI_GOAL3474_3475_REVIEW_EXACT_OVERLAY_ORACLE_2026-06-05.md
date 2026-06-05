# Gemini Review Handoff - Goal3474/3475 Exact Overlay Oracle

Please perform a read-only independent Gemini review of the Goal3474/3475
packet and write the review to:

- `docs/reviews/goal3476_gemini_review_exact_overlay_oracle_3474_3475_2026-06-05.md`

## Files To Inspect

- `scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py`
- `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_2026-06-05.md`
- `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json`
- `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.stdout`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `docs/reports/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_2026-06-05.md`
- `tests/goal3474_shape_pair_exact_overlay_area_shapely_oracle_test.py`
- `tests/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_test.py`

## Review Questions

1. Does Goal3474 correctly use Shapely/GEOS only as an external CPU correctness
   oracle, not as an RTDL runtime dependency or performance path?
2. Does the pod artifact support the stated exact target: 4,543 active relation
   rows, 1,090 positive exact-area rows, 3,453 zero-area rows, 0 exceptions,
   and total exact area 26.08321766231042?
3. Does Goal3475 update the v2.8 gap map honestly, preserving that the real
   remaining engineering work is a GPU-resident generic simple-polygon
   overlay-area continuation for nonconvex/high-vertex rows?
4. Are release, speedup, RT-core, true-zero-copy, RayJoin reproduction,
   RTDL-beats-RayJoin, and full overlay-completion claims still blocked?
5. Are there any correctness risks in the oracle policy, especially Shapely
   `make_valid` repair, row-order stability, or copying only ordinal columns?

## Required Verdict

Use exactly one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review should not edit source files other than the requested review output.
