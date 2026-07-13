# Goal4866 Result: RayJoin Section 5.7 Regression Hardening

Date: 2026-07-02

## Verdict Requested

`completed_goal4866_focused_regression_hardening__county_zipcode_byte_equal_guarded`

## Purpose

After Goal4859 achieved County x Zipcode byte-for-byte output equality against the AuthorPatch baseline, the immediate risk was regression: the decisive bugs were exposed by a 2.3G output comparison, which is too expensive to be the only guard.

Goal4866 adds focused local regression coverage for the main contracts exposed during Goal4859.

## Files Changed

Production:

- `src/rtdsl/rayjoin_overlay.py`

Tests:

- `tests/goal4866_rayjoin_section57_output_contract_test.py`

## Production Cleanup

Removed the now-dead segment-display helper code that had been created during debugging.

The final display model is now expressed by one rule:

- raw/rational intersection coordinates are preserved for identity;
- output display uses the author-style scaled-integer world-coordinate path;
- positive exact-half display uses a very narrow compatibility adjustment.

This avoids the earlier role-specific and endpoint-specific display heuristics.

## New Regression Tests

`tests/goal4866_rayjoin_section57_output_contract_test.py`

The test file adds four small, local tests:

1. `test_xsect_display_uses_author_internal_integer_path_not_endpoint_world_snap`

   Guards the case where endpoint-world snapping would emit `33.989950`, while the author-compatible internal-integer display emits `33.989949`.

2. `test_xsect_display_preserves_author_endpoint_like_negative_case`

   Guards the earlier negative endpoint-like case where display must be `-86.684939 34.080122` while raw identity prints `-86.684940 34.080122`.

3. `test_xsect_display_handles_negative_half_boundary_segment_case`

   Guards the negative half-boundary case where internal-integer display must emit `-75.054445 38.487071` while raw identity prints `-75.054446 38.487071`.

4. `test_streaming_writer_matches_materialized_writer_on_tiny_overlay`

   Builds a tiny CDB-like overlay in memory and verifies that the new streaming writer produces byte-identical text to the old materialized writer on the same input.

## Test Results

Command:

```text
py -m unittest tests.goal4866_rayjoin_section57_output_contract_test
```

Result:

```text
Ran 4 tests in 0.742s
OK
```

Combined command:

```text
py -m unittest tests.goal4866_rayjoin_section57_output_contract_test tests.goal4860_planar_map_lsi_row_materialization_test tests.goal4834_rayjoin_sos_synthetic_contract_test tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_sort_xsects_prefers_rational_distance_before_truncated_scaled_distance
```

Result:

```text
Ran 20 tests in 0.765s
OK (skipped=5)
```

The five skipped tests are OptiX-native tests skipped because local `RTDL_OPTIX_LIB` is not set. The new Goal4866 tests are pure local tests and all passed.

## What This Does Not Claim

- It does not rerun the 2.3G County x Zipcode POD byte-equality comparison.
- It does not reproduce another Section 5.7 pair.
- It does not authorize all eight Section 5.7 pairs.
- It does not authorize a performance claim.
- It does not claim Numba is central to this exact overlay-output path.

## Remaining P1

There is still duplication between:

- `_assemble_output_chains`
- `_write_output_chains_streaming`
- debug streaming/tracing scripts

The new tiny equivalence test reduces drift risk, but it does not fully remove it. A later refactor can extract shared chain-walk helpers, but that should be followed by a POD County x Zipcode byte-equality rerun because the production path is now known to be delicate.

## Recommended Next Step

Proceed to one of two next goals:

1. If exact inputs and AuthorPatch baseline are available for another Section 5.7 pair, start that pair.
2. If not, run a targeted data-availability audit and choose the next pair only when the baseline can be verified.

Do not claim full Section 5.7 until additional pairs pass the same production `sha256/cmp` gate.
