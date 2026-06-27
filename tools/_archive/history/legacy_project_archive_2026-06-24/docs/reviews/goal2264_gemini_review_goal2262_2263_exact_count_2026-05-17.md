# Independent Gemini Review for Goal2262/2263 Exact Count

This is an independent Gemini review, distinct from any Codex review.

## Review Questions and Answers

### 1. Does Goal2262 actually remove final membership-row allocation from the native count implementation while preserving exact GEOS/inclusive refinement?

**Yes.**
The `docs/reports/goal2262_exact_prepared_closed_shape_count_without_final_rows_2026-05-17.md` report explicitly states its purpose is to avoid allocating the final `RtdlPointClosedShapeMembershipRow` array in the native count path. It also confirms that the implementation "remains exact because it keeps the host GEOS/inclusive refinement step".

The `tests/goal2262_exact_prepared_closed_shape_count_without_final_rows_test.py` reinforces this:
- `test_count_path_no_longer_calls_row_return_path` asserts that the `count_prepared_point_closed_shape_membership_2d_optix` function body no longer calls `run_prepared_point_closed_shape_membership_2d_optix` or references `RtdlPointClosedShapeMembershipRow* rows`. It confirms the presence of `count_exact_hits` and `*count_out = exact_count`.
- `test_count_path_preserves_exact_refinement` asserts the presence of `prepared->right_geos->covers`, `exact_point_in_polygon`, and `download(chunk_rows.data()` within the count function body, indicating the preservation of host-side GEOS refinement.

### 2. Does Goal2263 evidence show exact count parity against the reference count?

**Yes.**
The `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md` report's "Timing Result" table shows "Count: 8,686" for both "prepared.run(...) row return" and "prepared.count(...) exact scalar count", with "Reference match: true" for both. The stated `reference_count` is 8,686.

The `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_2026-05-17.json` artifact confirms this with `"reference_count": 8686`, `"prepared_rows"."all_match_reference_count": true`, and `"prepared_count"."all_match_reference_count": true`. Both `prepared_rows.counts` and `prepared_count.counts` arrays contain only the value 8686.

The `tests/goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_test.py` file's `test_artifact_records_exact_count_parity` test explicitly asserts these equalities and boolean truths from the JSON artifact, confirming the parity.

### 3. Does the report support only the narrow claim that exact scalar count is faster than row-return materialization in this probe?

**Yes.**
The `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md` report clearly states: "The exact scalar count path is about `1.37x` faster than row-return materialization in this pushed-commit probe." It also notes a "small timing improvement" (`1.04x` faster) compared to a previous goal, emphasizing the "important semantic cleanup" as the primary achievement. The "Boundary" section of the report explicitly restricts claims to avoid broader generalizations.

The `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_2026-05-17.json` artifact shows `prepared_count.elapsed_sec_median` (0.0404...) is indeed less than `prepared_rows.elapsed_sec_median` (0.0552...).

The `tests/goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_test.py` file's `test_exact_count_is_faster_than_row_return` test asserts that `count_median` is less than `rows_median`, specifically `self.assertLess(count_median / rows_median, 0.75)`, which translates to a speedup greater than 1.33x, consistent with the reported 1.37x.

### 4. Does the report avoid claiming RayJoin reproduction, RTDL beating RayJoin, broad PIP speedup, v2.0 readiness, or true device-resident output streams?

**Yes.**
The `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md` report explicitly lists these disclaimers in its "Boundary" section:
- "a claim that RTDL beats RayJoin"
- "paper-scale RayJoin speedup claims"
- "broad PIP speedup claims"
- "v2.0 release readiness"
- "or a true device-resident output-stream claim."
The "Interpretation" section further clarifies: "This still is not a true device-resident output stream."

The `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_2026-05-17.json` artifact's `claim_boundary` field confirms that all these specific claims are unauthorized (set to `false`).

## Verdict

`accept`
