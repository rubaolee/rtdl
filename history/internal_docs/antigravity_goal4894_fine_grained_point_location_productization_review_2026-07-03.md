# Antigravity Review: Goal4894 Fine-Grained Directed Point-Location Productization

Date: 2026-07-03

## Verdict

`approve_goal4894_fine_grained_point_location_productized`

---

## Central Issue Assessment
Goal4894 is a **generic directed point-location planner productization**, not a RayJoin-specific shortcut.

Although the native C++ code contains legacy naming debt (`rayjoin_cdb` prefixing some parameters and internal enum/struct types), the actual algorithm modifies the range/AABB construction bounds of the public primitive `prepare_planar_map_point_location_2d_optix`. The implementation operates purely on geometric segment bounds and query point intersections. It does not inspect dataset names, schema configurations, or app identity. The generic nature is functional, as demonstrated by the non-RayJoin synthetic validation which successfully runs the primitive standalone.

---

## Verification Audit

1. **Fine-Grained No-Env Default**: Confirmed. In [rtdl_optix_workloads.cpp](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp#L4131-L4139), `rayjoin_cdb_group_mode_from_env()` defaults to `RayjoinCdbGroupMode::FineGrained` when `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE` and `RTDL_RAYJOIN_CDB_GROUP_MODE` are unset.
2. **Preservation of Override Routes**: Confirmed. The C++ parser correctly preserves legacy overrides `fixed8`/`fixed_8` (`Fixed8`), `adaptive` (`SequentialAdaptive`), and `block_merge64`/`author_block_merge64` (`BlockMerge64`) in [rtdl_optix_workloads.cpp](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp#L4140-L4154).
3. **Bundled Helper Max Iteration**: Confirmed. In [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L725-L730), `_directed_segment_point_location_grouping_env()` now sets `"RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER": "0"` (down from `"5"`) when auto-selecting `block_merge64` for extremely large workloads.
4. **Non-RayJoin Synthetic Evidence**: Confirmed. The summary JSON shows that 4 segments and 4 query points were processed via the generic public API without any RayJoin imports or overlay helpers, proving the primitive is fully decoupled.
5. **POD Result Honesty**: Confirmed. The report honestly details the tradeoff where map1 prepare/build cost increased by `~0.95s` (due to building a larger BVH structure over individual segments instead of grouped boxes), which was heavily offset by map1 run-time PIP traversal dropping from `2.929s` to `0.031s`, and map0 dropping from `35.617s` to `1.141s`.
6. **No Overclaiming**: Confirmed. The report contains a clear "What this does not claim" section explicitly disclaiming broad RTDL speedups, full Section 5.7 all-pair replication, or Numba acceleration on the primitive path.

---

## Answers to Review Questions

### 1. Does Goal4894 correctly productize the Goal4893 Route-A finding by making fine-grained directed point-location range construction the default, rather than relying on a manual env-var measurement route?
**Yes.** The fallback return value in the C++ environment parser is now set to `FineGrained`, meaning the system default is now optimized for candidate reduction without requiring manual environment variables.

### 2. Is the native planner change generic directed point-location work, or does it smuggle a RayJoin-only shortcut into the engine?
**It is generic.** The code does not query database tables, output-chain configurations, or application states. It operates entirely on geometric parameters of segment sequences, making it a general directed point-location range construction implementation.

### 3. Does the implementation preserve explicit override routes (`fixed8`, `adaptive`, `block_merge64`) while changing the no-env default to fine-grained?
**Yes.** All previously available modes are preserved and can still be manually requested using `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE` or the legacy `RTDL_RAYJOIN_CDB_GROUP_MODE`.

### 4. Is it acceptable that historical native names still contain `rayjoin_cdb`, given that the exposed behavior is public planar-map/directed point-location and the report discloses this naming debt?
**Yes.** The internal naming debt is acceptable for the v2.14 release prep review as renaming would touch too many non-functional areas of the codebase. The runtime behavior remains correctly isolated and generic.

### 5. Are the local and POD regression tests sufficient for Goal4894 closure?
**Yes.** 28 tests covering LSI, point-location, and SoS correctness were run locally and on the POD, passing successfully. Structural checks in [goal4894_directed_point_location_fine_grained_default_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal4894_directed_point_location_fine_grained_default_test.py) successfully assert the correct default routing behavior.

### 6. Does the non-RayJoin synthetic smoke show enough evidence that the public primitive is usable outside bundled RayJoin helper code?
**Yes.** The synthetic smoke test verifies that the public `prepare_planar_map_point_location_2d_optix` primitive successfully computes correct positive face mappings on a synthetic 4-segment polygon map without invoking any RayJoin package components.

### 7. Does the representative Section 5.7 POD result prove that the default no-env path now reaches the same correctness and performance class as the explicit Goal4893 best route?
**Yes.** The default no-env configuration achieved byte-for-byte correct output (SHA-256: `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`) in `92.773s`, compared to `93.345s` for the explicit Goal4893 best route and `129.448s` for the fixed8 default baseline.

### 8. Is the build-cost audit honest, especially the map1 prepare cost increase versus the much larger run-cost reduction?
**Yes.** The audit is completely transparent. It clearly shows a `~0.95s` build-time degradation on map1, but offsets it with a `2.9s` execution speedup, demonstrating a positive net trade-off.

### 9. Does the report avoid overclaiming broad RayJoin, Section 5.7 all-pair, or RTDL performance?
**Yes.** The report strictly bounds the performance claims to the Australia lakes x parks representative dataset and explicitly mentions that full Section 5.7 all-pairs replication and broad RTDL performance gains are not claimed.

### 10. Should Goal4894 close, and should the next performance goal move away from PIP range tuning toward CDB load/pack or LSI, based on the new phase breakdown?
**Yes.** Goal4894 has successfully resolved the candidate explosion blocker in the default engine settings. Future work should transition to addressing CDB load/pack (accounting for `~76.8s` of the total execution time) or LSI public rows (`~6.18s`), as point-location range tuning is now fully optimized.

---

## Authorization Boundaries check
This review does **not** authorize:
- Public release wording changes
- Broad RTDL performance claims
- Full RayJoin Section 5.7 all-pair claims
- Raw callback API usage
- V3/V4 resurrection as public release work
- Additional RayJoin-specific native kernels
