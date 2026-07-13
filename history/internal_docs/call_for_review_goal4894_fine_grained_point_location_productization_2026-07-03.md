# Call For Review: Goal4894 Fine-Grained Directed Point-Location Productization

Date: 2026-07-03

## Requested verdict label

Choose one:

- `approve_goal4894_fine_grained_point_location_productized`
- `approve_with_required_amendments`
- `block_as_rayjoin_specific_or_insufficiently_verified`

## Files to review

Primary report:

- `history/internal_docs/goal4894_fine_grained_point_location_productization_report_2026-07-03.md`

Code:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/rayjoin_overlay.py`
- `tests/goal4894_directed_point_location_fine_grained_default_test.py`

Artifacts:

- `history/internal_docs/goal4894_default_fine_grained_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4894_non_rayjoin_synthetic_point_location_summary_2026-07-03.json`

Prior evidence to compare:

- `history/internal_docs/goal4893_route_a_candidate_range_index_measurement_result_2026-07-03.md`
- `history/internal_docs/antigravity_goal4893_route_a_candidate_range_index_measurement_review_2026-07-03.md`

## Review questions

1. Does Goal4894 correctly productize the Goal4893 Route-A finding by making fine-grained directed point-location range construction the default, rather than relying on a manual env-var measurement route?

2. Is the native planner change generic directed point-location work, or does it smuggle a RayJoin-only shortcut into the engine?

3. Does the implementation preserve explicit override routes (`fixed8`, `adaptive`, `block_merge64`) while changing the no-env default to fine-grained?

4. Is it acceptable that historical native names still contain `rayjoin_cdb`, given that the exposed behavior is public planar-map/directed point-location and the report discloses this naming debt?

5. Are the local and POD regression tests sufficient for Goal4894 closure?

6. Does the non-RayJoin synthetic smoke show enough evidence that the public primitive is usable outside bundled RayJoin helper code?

7. Does the representative Section 5.7 POD result prove that the default no-env path now reaches the same correctness and performance class as the explicit Goal4893 best route?

8. Is the build-cost audit honest, especially the map1 prepare cost increase versus the much larger run-cost reduction?

9. Does the report avoid overclaiming broad RayJoin, Section 5.7 all-pair, or RTDL performance?

10. Should Goal4894 close, and should the next performance goal move away from PIP range tuning toward CDB load/pack or LSI, based on the new phase breakdown?

## Non-authorization boundaries

This review must not authorize:

- public release wording changes;
- broad RTDL performance claims;
- full RayJoin Section 5.7 all-pair claims;
- raw callback API;
- V3/V4 resurrection as public release work;
- additional RayJoin-specific native kernels.

It may authorize closing Goal4894 as a bounded post-v2.14 productization step if the evidence supports it.
