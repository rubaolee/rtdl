# Claude Review Handoff - Goal3477/3479 Overlay Complexity Contract

Please perform a read-only independent Claude review of Goals3477-3479 and
write the review to:

- `docs/reviews/goal3480_claude_review_overlay_output_complexity_contract_3477_3479_2026-06-05.md`

## Files To Inspect

- `scripts/goal3477_shape_pair_exact_overlay_output_complexity_oracle.py`
- `docs/reports/goal3477_shape_pair_exact_overlay_output_complexity_oracle_2026-06-05.md`
- `docs/reports/goal3477_shape_pair_exact_overlay_output_complexity_oracle_pod_2026-06-05.json`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `docs/reports/goal3478_v2_8_runtime_gap_after_overlay_output_complexity_2026-06-05.md`
- `tests/goal3478_v2_8_runtime_gap_after_overlay_output_complexity_test.py`
- `src/rtdsl/v2_8_overlay_area_continuation_contract.py`
- `docs/reports/goal3479_overlay_area_continuation_contract_2026-06-05.md`
- `tests/goal3479_overlay_area_continuation_contract_test.py`

## Review Questions

1. Does Goal3477 correctly characterize exact overlay output complexity from the
   external Shapely/GEOS oracle without treating Shapely as an RTDL runtime
   dependency?
2. Do the artifact values support the interpretation: 1,090 positive rows,
   609 positive `MultiPolygon` rows, 48 positive `GeometryCollection` rows,
   2,801 polygon components, 42,314 output vertices, max 22 components and
   586 output vertices in one row?
3. Does Goal3478 honestly update the gap map to split near-term scalar exact
   area from later streamed full-geometry output?
4. Does Goal3479 define a generic app-agnostic continuation contract with
   `scalar_exact_area` as P0 and `streamed_overlay_geometry` as P1?
5. Are all release, speedup, RT-core, true-zero-copy, paper reproduction,
   hidden dispatch, hidden partner selection, and full-overlay-completion claims
   still blocked?
6. What should the next implementation risk be before writing a GPU scalar-area
   kernel: numerical tolerance, topology repair, scratch-capacity policy,
   algorithm family, or device-resident payload layout?

## Required Verdict

Use exactly one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review should not edit source files other than the requested review output.
