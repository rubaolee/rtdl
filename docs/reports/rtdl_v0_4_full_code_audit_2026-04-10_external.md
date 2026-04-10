# External Claude v0.4 Full Code Audit

Date: 2026-04-10
Source path:

- `/Users/rl2025/claude-work/rtdl_v0_4_full_code_audit_2026-04-10.md`

## Scope Note

This report was produced from a parallel external audit checkout rooted at:

- `/Users/rl2025/claude-work/rtdl_review_2026-04-10-b`

It should therefore be read as external audit evidence, not as automatic proof
that every new artifact mentioned in that checkout was already present in the
main repo before import.

## Main Verdict

The external Claude audit says the `v0.4` nearest-neighbor line is:

- correct
- internally consistent
- ready for release tag creation

It reports:

- `109/109` tests passing in the external audit checkout
- no remaining blocking correctness issues
- confirmation that the historically important fixed-radius ordering bug and
  Embree `g_query_kind` bug were real and are already fixed in current history

## Important Additional Value

The most useful new artifact from this external audit is:

- `tests/goal_audit_knn_rows_contract_test.py`

That test file adds a 36-test contract-audit slice for `knn_rows`, covering:

- empty-input behavior
- no-padding behavior when `k` exceeds available neighbors
- neighbor-rank reset and contiguity
- tie-breaking at equal distance and at the `k` boundary
- output grouping by ascending `query_id`
- API validation for invalid `k`
- distance-field correctness
- baseline-contract mismatch/error cases
- external-baseline edge cases

## Follow-Through In Main Repo

This external audit artifact is preserved in the main repo history, and the
36-test `knn_rows` contract-audit file should be imported into the main repo as
the strongest direct technical follow-up from the audit.

## Raw Copy

The verbatim raw external report is preserved at:

- `docs/reports/external_raw/rtdl_v0_4_full_code_audit_2026-04-10.md`
