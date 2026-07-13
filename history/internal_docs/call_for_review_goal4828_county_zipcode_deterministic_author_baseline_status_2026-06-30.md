# Call For Review: Goal4828 County x Zipcode Deterministic Author Baseline Status

Please review:

`history/internal_docs/goal4828_county_zipcode_deterministic_author_baseline_status_2026-06-30.md`

Requested verdict labels:

- `approve_goal4828_status_and_authorize_streaming_prefix_compare`
- `approve_with_required_amendments`
- `block_until_correctness_record_fixed`

Review questions:

1. Is the deterministic author baseline generation correctly described and bounded to the same-source County x Zipcode dataset, not exact paper Section 5.7?
2. Is it correct to treat the old Goal4806 author output as a debug clue only, not deterministic ground truth?
3. Does the first-diff evidence correctly show that the previous RTDL full-output attempt diverged at byte 441 / line 25 with a face-id-only mismatch?
4. Is the correction to restore the author-source internal comparator while preserving author-reply `t_reported` perturbation justified by the author diff?
5. Is the public County x Soil byte-equality rerun sufficient regression evidence for the corrected comparator?
6. Is the no-output County x Zipcode summary useful as core-stage evidence while still not being a byte-equality proof?
7. Is performance correctly blocked?
8. Is the recommended next step correct: a corrected-build streaming/prefix comparison before any full performance work?

Non-authorization:

- This review must not authorize performance claims.
- This review must not authorize claiming full Section 5.7 reproduction.
- This review must not authorize using the old nondeterministic author output as truth.
- This review must not authorize RayJoin-only hidden kernels.
