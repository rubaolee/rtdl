# Goal1270 Polygon-Pair Candidate Diagnostic Reconciliation

Date: 2026-05-05

## Summary

Goal1263 and Goal1267 both preserved `candidate_count_matches_expected: false`
for `polygon_pair_overlap_area_rows` even when summary parity was true and
OptiX candidate discovery was faster than Embree. The issue is diagnostic
ambiguity: the existing field compares OptiX candidates against a conservative
candidate upper-bound/counting model, not directly against final positive
overlap rows.

Goal1270 keeps the old field for backward compatibility and adds explicit
positive-pair diagnostics.

## Added Fields

`scripts/goal877_polygon_overlap_optix_phase_profiler.py` now reports:

- `candidate_count_delta_vs_expected`
- `expected_positive_pair_count`
- `optix_positive_pair_count`
- `positive_pair_count_matches_expected`
- `comparison_note`

The old fields remain:

- `expected_or_cpu_candidate_row_count`
- `optix_candidate_row_count`
- `candidate_count_matches_expected`

## Interpretation

- `candidate_count_matches_expected` answers whether OptiX emitted the same
  number of candidate rows as the conservative candidate model.
- `positive_pair_count_matches_expected` answers whether OptiX produced the
  expected final positive overlap row count after exact continuation.

For the current authored polygon-pair workload, a false
`candidate_count_matches_expected` with true `positive_pair_count_matches_expected`
means the candidate model includes extra non-output candidates while final
summary parity still holds.

## Boundary

This does not broaden public wording. It makes the v1.2 diagnostic more precise
so future reviews can distinguish candidate upper-bound mismatch from final
positive-row correctness.

