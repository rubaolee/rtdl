Both the code and the doc contain the required language. The amendment is fully closed.

**`accept_goal4629_amendment_closed`**

---

**Amendment closure verified against actual repo files:**

**Code (`src/rtdsl/v4_weighted_sum_candidate_decision.py`, lines 105–114):** `future_promotion_requirements` tuple now includes:
- `"increase_repeat_count_to_release_gate_level_beyond_5_candidate_repeats"`
- `"measure_cupy_and_non_torch_partner_performance"`
- `"prove_triangle_counting_primary_route_release_coverage"`
This mirrors the three previously missing promotion blockers.

**Test (`tests/v4_goal4629_weighted_sum_candidate_decision_test.py`, lines 56–64):** `test_decision_preserves_device_output_metadata_and_promotion_blockers` contains explicit `assertIn` checks for:
- `"increase_repeat_count_to_release_gate_level_beyond_5_candidate_repeats"`
- `"measure_cupy_and_non_torch_partner_performance"`
- `"prove_triangle_counting_primary_route_release_coverage"`
These assertions verify programmatically that the requirements are present.

**Doc (`future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`, lines 107, 110, 111):** The "Future Promotion Requirements" section contains the corresponding human-readable items mirroring all blockers:
- "increase the repeat count to release-gate level beyond the five candidate repeats;"
- "measure CuPy and non-Torch partner performance if those partners are in scope;"
- "prove triangle-counting primary-route release coverage instead of relying on adjacent grouped-reduction coverage;"

All three files (code, test, doc) carry the required explanation. The single required amendment is closed with no gaps, and all non-authorization boundaries are fully preserved.
