Both the code and the doc contain the required language. The amendment is fully closed.

**`accept_goal4627_coverage_audit`**

---

**Amendment closure verified against actual repo files:**

**Code (`src/rtdsl/v4_coverage_audit.py`, lines 185–189):** `triangle_counting.release_gap` now reads exactly as required — "The measured grouped-i64 operator covers an adjacent grouped-reduction dimension, but not triangle counting's dominant any-hit weighted/count continuation path. That primary route is the weighted-sum candidate and needs Goal4629 promotion/rejection review."

**Test (`tests/v4_goal4627_coverage_audit_test.py`, lines 80–81):** `test_rejects_app_identity_and_candidate_shortcuts` asserts both `"adjacent grouped-reduction dimension"` and `"dominant any-hit weighted/count continuation path"` are present in the `release_gap` field. These assertions are machine-checkable and would fail if the explanation were removed or weakened.

**Doc (`future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`):** Line 60 contains the mirrored sentence in the coverage table's release gap column for `triangle_counting`.

All three surfaces (code, test, doc) carry the required explanation. The single required amendment is closed with no gaps.
