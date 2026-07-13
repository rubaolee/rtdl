# Call For Review: Goal4896 LSI Pair-ID Rows Optimization

Please review:

- `history/internal_docs/goal4896_lsi_pair_id_rows_optimization_report_2026-07-03.md`
- Code changes in:
  - `src/native/optix/rtdl_optix_prelude.h`
  - `src/native/optix/rtdl_optix_api.cpp`
  - `src/native/optix/rtdl_optix_workloads.cpp`
  - `src/rtdsl/optix_runtime.py`
  - `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
  - `history/internal_docs/goal4893_measurement_wrapper.py`
  - `tests/goal4851_planar_map_lsi_public_front_door_test.py`
- Evidence JSON:
  - `history/internal_docs/goal4896_lsi_probe_summary_2026-07-03.json`
  - `history/internal_docs/goal4896_old_lsi_control_overlay_summary_2026-07-03.json`
  - `history/internal_docs/goal4896_pair_id_rows_overlay_summary_2026-07-03.json`

## Requested verdict labels

Choose one:

- `approve_goal4896_generic_lsi_pair_id_rows_optimization`
- `approve_with_required_amendments`
- `block_as_rayjoin_specific_or_claim_overreach`
- `fail_redo`

## Questions

1. Is `run_pair_id_rows()` a legitimate generic planar-map LSI result shape, rather than a RayJoin-specific hidden shortcut?
2. Does the implementation preserve old full-row behavior through `run_raw()` while adding a lightweight pair-id path for users that only need ids?
3. Is it correct that the old path paid unnecessary native exact-refine/materialization cost for this harness because downstream code only consumes `left_id/right_id`?
4. Are the performance claims properly bounded: about 1.9x on the LSI stage and about 1.17x on the same-wrapper hot-cache representative overlay, with byte equality preserved?
5. Does the evidence avoid cache-temperature overclaiming by including a same-wrapper old-LSI control?
6. Are the local and POD tests sufficient for this bounded goal, or should another test be required before closing?
7. Does the report correctly avoid claiming full Section 5.7, broad RayJoin speedup, or AuthorOfficial overall performance win?
8. Should Goal4896 close with label `completed_generic_lsi_pair_id_rows__representative_overlay_byte_equal__bounded_speedup`?

## Non-authorization boundaries

This review must not authorize:

- full Section 5.7 eight-pair reproduction claims,
- broad RTDL/RayJoin performance claims,
- any claim that RTDL beats AuthorOfficial overall,
- raw OptiX callback exposure,
- app-identity RayJoin kernels in RTDL core,
- V3/V4 release claims.
