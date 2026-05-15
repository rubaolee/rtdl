# Goal2068/2069 Final v2.0 Matrix + Pre-Release Gate Review Request

Please perform a read-only external review of the v2.0 release-hardening packet in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

Review these files:

- `docs/reports/goal2068_final_v2_0_release_matrix.json`
- `docs/reports/goal2068_final_v2_0_release_matrix.md`
- `scripts/goal2068_final_v2_0_release_matrix.py`
- `tests/goal2068_final_v2_0_release_matrix_test.py`
- `docs/reports/goal2069_v2_0_pre_release_gate.json`
- `docs/reports/goal2069_v2_0_pre_release_gate_2026-05-15.md`
- `scripts/goal2069_v2_0_pre_release_gate.py`
- `tests/goal2069_v2_0_pre_release_gate_test.py`
- Supporting latest evidence from Goal2066:
  - `docs/reports/goal2066_v2_pod_large_scale_followup_2026-05-15.md`
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

1. Goal2068 correctly updates the final v2.0 matrix after Goal2066:
   - `robot_collision_screening` is no longer mixed and uses the 32768/65536 positive evidence.
   - `segment_polygon_hitcount`, `road_hazard_screening`, and fixed-radius rows use the stronger Goal2066 large-scale evidence.
   - `segment_polygon_anyhit_rows` remains the only mixed row due to full witness-row materialization being slower.
   - `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` remain bounded because 4096 OptiX candidate discovery OOMs and naive streaming was rejected as a parity failure.
2. Goal2069 is a valid pre-release engineering gate:
   - final matrix status is checked;
   - public v2 claim scan passes;
   - focused unittest slice passes (`40 tests, 1 skipped`);
   - native app-agnostic/purity and partner architecture tests are included.
3. The packet does not overclaim:
   - no v2.0 release authorization;
   - no all-app speedup claim;
   - no broad RT-core speedup claim;
   - no arbitrary partner-program acceleration claim;
   - no package-install claim;
   - no full witness-row materialization solved claim;
   - no scalable arbitrary polygon overlay solved claim.
4. The deferred lanes are correctly kept outside v2.0:
   - Goal2025 Triton/Numba;
   - Goal2037 Embree CPU partner all-thread lane;
   - v3.0 custom engine extensions.

Write the review to:

`docs/reviews/goal2070_gemini_review_goal2068_2069_final_v2_gate_2026-05-15.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `reject`, or `needs-more-evidence`. Expected likely verdict is `accept-with-boundary` if the packet is sound but still awaits final Claude review and final 3-AI release consensus.
