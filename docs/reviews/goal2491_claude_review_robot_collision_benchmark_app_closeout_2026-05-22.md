All files verified. Here is the review.

---

## Goal2491 Robot-Collision Benchmark App Closeout — Review

### Verdict: **APPROVE**

No blocking issues. One minor dead-code observation, documented below.

---

### 1. Technical Honesty

Passes. Every number in the closeout markdown traces directly to the pod summary JSON:

| Mode | Closeout (s) | JSON (s) | Match |
|---|---|---|---|
| cpu_reference | 0.3339872658252716 | 0.3339872658252716 | ✓ |
| embree_prepared | 0.008597038686275482 | 0.008597038686275482 | ✓ |
| embree_prepared_buffers | 0.00010654330253601074 | 0.00010654330253601074 | ✓ |
| optix_prepared | 0.006283417344093323 | 0.006283417344093323 | ✓ |
| optix_prepared_buffers | 0.0001258254051208496 | 0.0001258254051208496 | ✓ |
| optix_prepared_device_buffers | 8.090585470199585e-05 | 8.090585470199585e-05 | ✓ |
| optix_prepared_device_count | 5.284696817398071e-05 | 5.284696817398071e-05 | ✓ |

All four internal ratios in the performance interpretation section are arithmetically correct against the pod timing values (49.94x, 1.56x, 1.53x, 80.69x — verified).

Notably, **no cpu_reference-vs-native ratio is published**, which is the right call. The language "internal exact-subpath ratios only" is precise and sufficient.

The local matrix honestly records OptiX rows as `"status": "skipped", "reason": "optix_disabled"` and documents the Mac Python environment requirement. No overclaim.

---

### 2. App/Native Boundary

Passes. Three independent checks converge:

- **App code**: `_claim_boundary()` sets `native_robot_abi_added: False`, `native_collision_abi_added: False`, `native_engine_touch_kind: "generic_rt_primitive_only"` for every non-reference mode. Native API calls are `prepare_embree_static_triangle_scene_3d`, `run_grouped_segment_any_hit_flags`, etc. — generic throughout.
- **Grep on `src/native/embree/` and `src/native/optix/`**: Zero hits for the forbidden vocabulary regex `\b(robot|collision|link|pose|joint|kinematic|planner)\b`. A hit does appear in `src/native/vulkan/rtdl_vulkan_core.cpp` but that directory is outside the test scope and Goal2491.
- **Test `test_native_files_remain_app_vocabulary_free`**: Correctly scoped to the two active directories; will pass.

---

### 3. Final Matrix — Internal Exact-Subpath Claims Only

Passes. The `claim_boundary` block is present at three levels: top-level in `summary.json`, inside every `prepared_query_descriptor`, and in the `run_performance_matrix()` return value in the app. All instances are consistent:

```json
"public_speedup_claim_authorized": false,
"paper_reproduction_claim_authorized": false,
"authors_code_comparison_claim_authorized": false,
"internal_evidence_only": true
```

The `matrix_scope: "final_canonical_robot_collision_modes"` label is correctly set when `--final-matrix` is passed (app line 1093–1095), and the goal tag is set to `"Goal2491"` (line 1134).

---

### 4. Unsupported Claims

Passes. The closeout has a nine-item explicit "Unsupported Contract" section. All prohibited claims are machine-readable in JSON. The `_paper_status()` function in the app explicitly marks `official_code_verified: False` and `official_data_verified: False`, and directs any future authors-code comparison to a separate scoping goal. No wording in the closeout implies a whole-application claim or paper comparison.

---

### 5. Test Coverage

All four tests will pass against the current artifacts:

- `test_goal_and_report_record_finish_scope` — goal file exists at `docs/reports/goal2491_finish_robot_collision_benchmark_app_goal_2026-05-22.md` and contains "Finish the robot-collision benchmark app". ✓
- `test_app_exposes_final_matrix_modes` — all seven canonical modes present in the app, `--final-matrix` and `final_canonical_robot_collision_modes` present. ✓
- `test_pod_summary_records_all_final_rows` — all 7 rows `status: "ok"`, correctness flags true, `optix_prepared_device_count` descriptor fields correct. ✓
- `test_native_files_remain_app_vocabulary_free` — embree and optix native files clean. ✓

---

### Minor Observations (Non-Blocking)

1. **Dead code in `run_robot_collision_benchmark`** (app lines 607–608): for `optix_prepared_device_buffers`, `mode.endswith("_prepared_buffers")` is `True`, so `backend` would resolve to `"optix_prepared_device"` — wrong. However, `main()` routes both device-buffer modes directly to `run_prepared_reuse_probe` before the generic branch, so this code is never reached. Harmless but messy.

2. **SSH credentials in closeout doc**: IP, port, and key path are embedded in the pod command block. Intentional for reproducibility; not a technical honesty issue.

3. **`pod_final_matrix.json`** listed as an artifact — verified to exist at `docs/reports/goal2491_robot_collision_finish_pod/pod_final_matrix.json`. ✓

---

### Conclusion

Goal2491 is **technically honest**, the native boundary is **app-agnostic and enforced by test**, the matrix **supports only internal exact-subpath claims**, unsupported claims are **clearly and redundantly excluded**, and all artifacts are consistent. Goal2491 can be closed. The 2-AI consensus requirement noted in the closeout applies to project closure; this review counts as one.
