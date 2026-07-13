# Call For Review: Goal4895 Generic Packed CDB Input Cache

Date: 2026-07-03

## Requested verdict label

Choose one:

- `approve_goal4895_packed_cdb_cache_productized`
- `approve_with_required_amendments`
- `block_as_app_specific_cache_or_insufficiently_verified`

## Files to review

Primary report:

- `history/internal_docs/goal4895_planar_map_cdb_packed_cache_report_2026-07-03.md`

Code:

- `src/rtdsl/datasets.py`
- `src/rtdsl/__init__.py`
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
- `tests/goal4895_planar_map_cdb_packed_loader_test.py`
- `tests/goal4895_public_cdb_loader_harness_integration_test.py`

Artifacts:

- `history/internal_docs/goal4895_cache_cold_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4895_cache_warm_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4894_default_fine_grained_overlay_summary_2026-07-03.json`

## Review questions

1. Is `load_planar_map_cdb_packed_inputs` a generic CDB/planar-map input utility, or is it a RayJoin-specific cache hidden behind a generic name?

2. Does the loader stay in data input/packing scope, without doing LSI, PIP, overlay assembly, duplicate-half-edge policy, or Section 5.7 application logic?

3. Is it acceptable to expose this as public RTDL data utility while the downstream paper-reproduction app remains application code?

4. Are the cache key and invalidation inputs sufficient for this bounded goal: source size, source mtime, and format version?

5. Are the local/POD tests sufficient for closure?

6. Does the Goal4880 harness integration correctly replace duplicated private load/pack code with the public loader?

7. Do the cold and warm POD results prove a real end-to-end improvement while preserving byte equality?

8. Is the interpretation honest that this improves repeat runs and vectorized load/pack, but does not solve data acquisition or full Section 5.7 all-pair reproduction?

9. Does the report avoid overclaiming broad RTDL, broad RayJoin, or public release guarantees?

10. Should Goal4895 close, and should the next performance target move to LSI traversal/refinement?

## Non-authorization boundaries

This review must not authorize:

- broad public performance claims;
- full Section 5.7 all-pair claims;
- V3/V4 resurrection;
- RayJoin-specific native kernels;
- changes to public release wording;
- claims that first-ever data acquisition or source conversion is solved.

It may authorize closing Goal4895 as a bounded post-v2.14 engineering step if evidence supports it.
