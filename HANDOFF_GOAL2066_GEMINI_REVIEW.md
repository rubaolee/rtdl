# Goal2066 External Review Request

Please perform a read-only Gemini review of Goal2066 in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

Review these files:

- `docs/reports/goal2066_v2_pod_large_scale_followup_2026-05-15.md`
- `tests/goal2066_v2_pod_large_scale_followup_test.py`
- `docs/reports/goal2066_robot_collision_cupy_l4_32768x8192.json`
- `docs/reports/goal2066_robot_collision_cupy_l4_65536x8192.json`
- `docs/reports/goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json`
- `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json`
- `docs/reports/goal2066_road_hazard_cupy_l4_12288_prepared_only.json`
- `docs/reports/goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log`

Please verify:

1. The reported positive scaling rows are numerically grounded:
   - robot collision 32768 and 65536 are faster than v1.8 prepared;
   - segment/polygon hitcount 131072 is strongly faster through compact count columns;
   - road hazard 12288 prepared-only is faster than v1.8 prepared;
   - fixed-radius 16384 rows remain strongly positive but are threshold/proxy rows only.
2. The negative/mixed rows are represented honestly:
   - full segment/polygon any-hit row materialization remains slower;
   - polygon pair overlap remains slower at 2048/3072;
   - polygon Jaccard is only near parity/slightly faster;
   - 4096 polygon control fails in OptiX candidate discovery with CUDA out-of-memory and should be treated as a scaling blocker, not a timing row.
3. The report does not overclaim:
   - no v2.0 release readiness;
   - no all-app speedup claim;
   - no full witness-row materialization solved claim;
   - no complete polygon overlap/Jaccard scalable primitive claim.
4. The test assertions match the evidence and preserve the release boundary.

Write your review to:

`docs/reviews/goal2067_gemini_review_goal2066_large_scale_v2_pod_followup_2026-05-15.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `reject`, or `needs-more-evidence`. Expected likely verdict is `accept-with-boundary` if the evidence and boundaries are correct.
