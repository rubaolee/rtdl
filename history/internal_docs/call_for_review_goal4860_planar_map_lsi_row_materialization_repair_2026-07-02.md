# Call For Review: Goal4860 Planar-Map LSI Row Materialization Repair

Date: 2026-07-02

Please critically review Goal4860.

## Files To Review

- `history/internal_docs/goal4860_planar_map_lsi_row_materialization_repair_result_2026-07-02.md`
- `history/internal_docs/goal4860_county_zipcode_lsi_row_gate_summary.json`
- `history/internal_docs/goal4860_au_lsi_row_gate_summary.json`
- `tests/goal4860_planar_map_lsi_row_materialization_test.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`

## Context

Goal4859 attempted to proceed toward RayJoin Section 5.7, but found that the
public planar-map LSI scalar count and LSI rows did not share the same contract.

That exposed a Section 5.2 bug:

- scalar count worked;
- rows missed intersections;
- a minimal witness returned `count=2, rows=0`.

Goal4860 repairs the public planar-map LSI row path so rows are materialized
from the same predicate/traversal contract used by the count path.

## Requested Verdict Labels

Choose one:

- `approve_goal4860_lsi_row_repair_and_resume_section57`
- `approve_with_required_amendments_before_section57`
- `reject_goal4860_as_rayjoin_specific_or_insufficient`

## Questions

1. Is this correctly classified as a Section 5.2 LSI row-materialization bug,
   rather than a Section 5.3/PIP bug?
2. Does the implementation repair a generic public planar-map LSI row contract,
   rather than hiding a RayJoin application shortcut?
3. Is it acceptable that row materialization now uses the same grouped-range
   predicate route as the scalar count path?
4. Are the synthetic witnesses sufficient to show the previously missing row
   categories: endpoint, endpoint tolerance, endpoint-on-segment, and
   near-collinear overlap?
5. Does the County x Zipcode evidence prove `count == rows == expected == 961165`
   on the correct large input?
6. Does the Australia representative evidence prove
   `count == rows == expected == 13622`?
7. Are the claim boundaries correct: no Section 5.3/PIP claim, no Section 5.7
   overlay claim, and no performance claim?
8. Are additional gates required before resuming Section 5.7 from repaired LSI
   rows?

## Non-Authorization

This review must not authorize:

- Section 5.3/PIP correctness;
- Section 5.7 overlay correctness;
- Section 5.7 performance;
- broad RayJoin paper reproduction;
- broad RTDL performance.
