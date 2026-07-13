# Call For Review: Goal4851 Explicit Predicate ABI Follow-Up

Date: 2026-07-01

## Requested Verdict

Please return one of:

- `approve_goal4851_explicit_predicate_abi_closes_am2`
- `approve_with_required_amendments`
- `block_goal4851_explicit_predicate_abi`

## Context

Claude's Goal4851 review approved the public planar-map LSI primitive with
required amendments. AM2 warned that predicate selection through
`RTDL_OPTIX_SEGMENT_PAIR_PREDICATE` was process-global and therefore unsafe for
a public primitive.

This follow-up changes the public `prepare_planar_map_lsi_2d_optix` path to use
an explicit native predicate-mode parameter instead of Python env-var mutation.

Primary report:

- `history/internal_docs/goal4851_explicit_predicate_abi_followup_2026-07-01.md`

Primary artifacts:

- `history/internal_docs/goal4851_explicit_predicate_build.log`
- `history/internal_docs/goal4851_explicit_predicate_metadata.json`
- `history/internal_docs/goal4851_explicit_predicate_synthetic_stdout.json`

Code paths to inspect:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `tests/goal4851_planar_map_lsi_public_front_door_test.py`

## Review Questions

1. Does the new native symbol
   `rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode`
   remove the process-global env-var predicate selection from the public
   planar-map LSI route?
2. Does the old env-var path remain only as backward-compatible legacy behavior
   for old/raw native entrypoints, rather than being used by
   `prepare_planar_map_lsi_2d_optix`?
3. Does the POD evidence prove the new symbol builds and is actually called by
   the metadata smoke?
4. Does the synthetic probe preserve the semantic delta between raw segment-pair
   counting and planar-map LSI after the ABI change?
5. Do the tests correctly fail if the public front door starts mutating
   `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE` again?
6. Does this close AM2, or is there still a blocker before Goal4851 can be
   treated as an approved public count-only primitive?
7. Are the claim boundaries still correct: count-only LSI, no full overlay,
   no broad RayJoin/Section 5.7 reproduction claim, and no broad speedup claim?

## Non-Authorization

This review must not authorize:

- full RayJoin overlay reproduction,
- Section 5.7 paper reproduction,
- public speedup wording,
- complete V3/V4 release claims,
- or any unrelated runtime/native changes.
