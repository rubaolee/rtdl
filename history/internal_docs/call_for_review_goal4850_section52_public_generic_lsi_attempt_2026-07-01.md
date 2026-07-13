# Call For Review: Goal4850 Section 5.2 Public Generic LSI Attempt

Date: 2026-07-01

## Requested Verdict

Please review Goal4850 and choose one:

- `approve_goal4850_public_generic_lsi_gap`
- `reject_goal4850_public_generic_route_was_wrong`
- `needs_more_evidence_before_gap_label`

## Files To Review

- Goal document: `history/internal_docs/goal4850_section52_lsi_public_generic_rtdl_app_goal_2026-07-01.md`
- User-mode script: `history/internal_docs/goal4850_rayjoin_section52_lsi_public_primitives.py`
- Run artifact: `history/internal_docs/goal4850_current_osm_au_public_primitives_summary.json`
- Result report: `history/internal_docs/goal4850_section52_lsi_public_generic_rtdl_app_result_2026-07-01.md`
- Next proposed goal: `history/internal_docs/goal4851_public_cdb_lsi_primitive_contract_goal_2026-07-01.md`

## Context

The user asked why Section 5.2 LSI has not been made into:

> a normal user-written RayJoin implementation using public generic RTDL primitives plus Numba

For Section 5.2 LSI count, Numba should not be required in the hot path; the natural public route is RTDL's generic prepared segment-pair OptiX primitive. Goal4850 tested that route without importing the bundled `rtdsl.rayjoin_overlay` helper.

## Key Evidence

The script imported only:

- `rtdsl.load_cdb`
- `rtdsl.chains_to_rayjoin_cdb_segments`
- `rtdsl.optix_runtime.prepare_segment_pair_intersection_optix`
- `rtdsl.optix_runtime.prepare_segment_pair_left_set_optix`

It did not import `rtdsl.rayjoin_overlay`.

On the current OSM Australia lakes/parks representative pair:

- expected AuthorPatch/RayJoin LSI count: `13622`
- public generic prepared segment-pair count: `103869`
- matched expected: `false`

The full JSON artifact records:

```json
{
  "count": 103869,
  "expected_count": 13622,
  "matched_expected": false,
  "bundled_rayjoin_helper_used": false,
  "public_generic_rtdl_primitives": true
}
```

## Reviewer Questions

1. Does the script genuinely avoid bundled/private RayJoin helper usage?
2. Is it fair to classify this as a public primitive contract gap rather than a Python user-code mistake?
3. Is the result enough to say that raw segment-pair exact count is not the same as Section 5.2 LSI?
4. Is Goal4851 the right next step: identify the semantic delta and promote a public generic CDB/planar-map LSI primitive?
5. Should Numba be required for Section 5.2 LSI, or is it correct to keep Numba for later continuation/topology stages?
6. Does this finding leave the earlier bundled-helper Section 5.2 reproduction intact but bounded?

## Non-Authorization

This review must not authorize:

- full Section 5.7 overlay reproduction claims
- all eight exact paper pair claims
- broad RTDL performance claims
- any claim that current public generic primitives already reproduce Section 5.2 LSI
- hidden RayJoin-specific core shortcuts
