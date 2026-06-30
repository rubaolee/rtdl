# Call For Review: Goal4816-B RayJoin v2.14 Capability Map

Date: 2026-06-30

Review target:

`history/internal_docs/goal4816_B_rayjoin_v2_14_asset_capability_map_2026-06-30.md`

Prior gate:

`history/internal_docs/antigravity_goal4816_A_contract_extraction_review_2026-06-30.md`

## Requested Verdict Labels

Use one of:

- `approve_goal4816_B_capability_map_authorize_4816_C`;
- `approve_with_required_amendments_before_4816_C`;
- `block_goal4816_B_redo_capability_map`;
- `block_goal4816_line_due_to_v2_14_capability_or_input_gap`.

## Review Questions

1. Does the map correctly separate `existing_v2_14_primitive`,
   `bundled_rayjoin_helper`, `numba_partner_continuation`, `paper_app_logic`,
   `missing_input`, and `unresolved_pip_tie_break_contract`?
2. Does it correctly classify `prepare_segment_pair_intersection_optix` and
   `prepare_segment_pair_left_set_optix` as generic/existing prepared LSI
   primitives while classifying `_run_lsi_rows` as bundled RayJoin helper row
   reconstruction?
3. Does it correctly classify `prepare_directed_segment_point_location_2d_optix`
   as an exposed directed point-location primitive with RayJoin policy caveats,
   while classifying `_PreparedPointLocationRunner` as bundled helper?
4. Does it correctly avoid claiming the current native
   `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES` / `nextafterf` behavior as the author's
   slope-dependent `t_reported` formula?
5. Does it correctly state that full 8/8 Section 5.7 remains blocked by missing
   exact CDB inputs in the current POD state?
6. Does it correctly preserve historical Goal4380 as 2/8 bounded evidence and
   avoid treating it as full reproduction?
7. Does it correctly state that generic-primitive + Numba full Section 5.7 is
   not yet proven, while bundled-helper bounded reproduction is feasible?
8. Does the recommended Goal4816-C split into two routes prevent hidden runtime
   edits and bundled-helper laundering?
9. Are any claimed assets misclassified, missing, or overstated?
10. Should Goal4816-C be authorized as an app-only design goal, or must
    Goal4816-B be amended first?

## Non-Authorization Boundaries

This review must not authorize:

- modifying `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface;
- running POD performance experiments;
- adding a new RayJoin-specific runtime primitive;
- presenting bundled-helper output as generic RTDL language reproduction;
- claiming full 8/8 Section 5.7 reproduction;
- treating scalar LSI/PIP, Numba compact-mask, or side-aware topology preview as
  full polygon overlay reproduction.

## Expected Reviewer Output

Please provide:

- one verdict label;
- P0/P1/P2 findings;
- answers to the ten review questions;
- explicit statement whether Goal4816-C is authorized;
- explicit non-authorization block.
