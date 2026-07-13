# Call For Review: Goal4859 LSI Row-Surface Gap And Goal4860 Plan

Date: 2026-07-02

## Files To Review

- `history/internal_docs/goal4859_section57_lsi_row_surface_gap_report_2026-07-02.md`
- `history/internal_docs/goal4860_planar_map_lsi_row_materialization_repair_goal_2026-07-02.md`
- `history/internal_docs/goal4859_minimal_real_witness_probe_summary.json`
- `history/internal_docs/goal4859_au_chunk_mismatch_locator_summary.json`
- `history/internal_docs/goal4859_county_zipcode_correct_input_hidden_predicate_lsi_rows_summary.json`

## Context

Goal4859 attempted to proceed toward RayJoin Section 5.7 County x Zipcode
correctness-first reproduction using public RTDL primitives/app-layer logic
where possible.

The run found a blocker before PIP/point-location and before full overlay:

`planar_map_lsi_count` and row materialization do not agree.

The strongest minimal witness is a three-segment case extracted from the
Australia representative pair:

- public planar-map LSI scalar count: `2`
- hidden-predicate row materialization count: `0`

This means the old Section 5.2 count-only gate is insufficient for Section 5.7.
Section 5.2 needs a row-contract gate before Section 5.7 can continue.

## Requested Verdict Labels

Choose one:

- `approve_goal4859_pause_section57_and_authorize_goal4860_lsi_row_repair`
- `request_amendments_before_goal4860`
- `reject_gap_diagnosis_continue_section57_without_lsi_row_repair`

## Questions For Reviewer

1. Does the evidence justify classifying the current blocker as an LSI
   row-surface contract gap rather than a PIP/Section 5.3 bug?

2. Is it correct that Section 5.2 count-only reproduction remains valid, but
   Section 5.2 now needs an additional row-materialization gate for Section 5.7?

3. Does the minimal witness (`count=2`, `rows=0`) provide a sufficiently small,
   controlled regression case?

4. Is it correct to pause Section 5.7 full overlay and performance work until
   the LSI row path matches the scalar count path?

5. Is Goal4860 scoped correctly as a generic planar-map LSI row repair rather
   than a RayJoin-specific application patch?

6. Are the Goal4860 exit gates sufficient?

   - minimal witness: rows `2`;
   - Australia representative: rows `13622`;
   - correct County x Zipcode input: rows `961165`.

7. Should PIP/Section 5.3 remain out of scope until LSI rows are correct?

8. Do you authorize Goal4860 to start, with the understanding that any
   runtime/native repair must be generic and externally reviewed before
   closure?

## Non-Authorization

This review request does not authorize:

- Section 5.7 completion claims;
- Section 5.7 performance claims;
- full eight-pair paper reproduction claims;
- treating raw segment-pair rows as planar-map LSI rows;
- RayJoin-specific hidden kernel patches;
- moving to PIP/point-location debugging before LSI rows are repaired.
