# Goal2809 Gemini Review: Hausdorff Warm/Tuned v2.5 Entrypoint (2026-05-31)

## Verdict: accept-with-boundary

## Findings:

### 1. Cold-start measurement flaw fix:
- **Files inspected:**
    - `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py`
    - `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
    - `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- **Analysis:**
  The report `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md` explicitly states that Goal2809 fixes a measurement flaw where the RTDL/OptiX path was timed cold while the CuPy baseline was warmed. The `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` script confirms that `DEFAULT_RTDL_WARMUP = 1` and `DEFAULT_REPEAT = 3` are set. The `run_goal2801_hausdorff_entrypoint` function in this script includes explicit `baseline_warmup_started` and `rtdl_warmup_elapsed_sec` timings, indicating warming for both paths. Additionally, the `_median_by_elapsed` function is used for both baseline and RTDL runs, confirming repeated median timing. The `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py` validates these settings in `test_script_records_warmup_repeat_and_tuned_adaptive_metadata`. This confirms that the cold-start measurement flaw is addressed by warming RTDL and using repeated median timing for both paths.

### 2. Pod artifact exactness, provenance, and reporting:
- **Files inspected:**
    - `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_pod/hausdorff_xhd_v25_warm_median_4096.json`
    - `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md`
- **Analysis:**
  The pod artifact `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_pod/hausdorff_xhd_v25_warm_median_4096.json` explicitly states `"matches_exact_baseline": true` and `"distance_error": 0.0`, confirming exactness. Its provenance is clean with `"source_commit": "b328b9b3aafc14a862f1287a2948fa47474fe690"` and `"source_dirty": []`. The artifact reports `"rtdl_over_cupy_grid_elapsed_ratio": 17.558764307472902`, which is consistently presented in `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md` as "17.558764x" slower. Both the report and the artifact correctly frame this as RTDL still being slower than CuPy, stating it's a "benchmark-quality improvement, not a performance victory." The `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py` file includes `test_pod_artifact_is_exact_bounded_and_faster_than_old_cold_artifact`, which asserts these properties.

### 3. Adaptive defaults genericity:
- **Files inspected:**
    - `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
    - `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- **Analysis:**
  The file `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py` defines `default_adaptive_target_points_per_group()` which uses `default_target_points_per_group()` described as a "scale-aware default for grouped point-set RT traversal," without Hausdorff-specific naming. The function `hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness` in the same file accepts `growth_factor` and `target_points_per_group` as parameters, implying configurability rather than hardcoded specific behavior. The `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` sets `DEFAULT_ADAPTIVE_GROWTH_FACTOR = 8.0` and `DEFAULT_ADAPTIVE_TARGET_POINTS_PER_GROUP = 512`, and its `CLAIM_BOUNDARY` explicitly flags `"native_engine_customization": False`. The main report (`docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md`) mentions that the work is "generic runtime work, not a Hausdorff-specific native engine shortcut," and `docs/research/future_version_to_do_list.md` also explicitly states, "Do not reintroduce Hausdorff-specific native ABI names." This evidence confirms that the adaptive defaults are generic and do not reintroduce Hausdorff-specific native ABI/custom engine behavior.

### 4. Public speedup, whole-app, broad RT-core, X-HD reproduction, and release-authorization claim flags:
- **Files inspected:**
    - `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md`
    - `docs/research/future_version_to_do_list.md`
- **Analysis:**
  The `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md` report contains a dedicated "Claim Boundary" section that explicitly closes all relevant flags: "No public speedup claim is authorized," "No RTDL-beats-CuPy claim is authorized," "No RTDL-beats-X-HD claim is authorized," "No paper reproduction claim is authorized," "No broad RT-core speedup claim is authorized," "No whole-app speedup claim is authorized," and "No native engine customization is introduced." The pod artifact `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_pod/hausdorff_xhd_v25_warm_median_4096.json` corroborates this by setting all corresponding boolean flags within its `"claim_boundary"` field to `false`. The `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py` further validates this in `test_claim_flags_remain_false`, which asserts that these claim flags are indeed `false` in the artifact. This demonstrates a consistent and explicit effort to keep all such claims closed.

### 5. Stale wording, overclaim, missing evidence, or test/report mismatch:
- **Files inspected:**
    - All of the above.
- **Analysis:**
  A comprehensive review of all provided files reveals no stale wording, overclaims, missing evidence, or test/report mismatches. The `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md` report is consistent with the code changes in `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` and `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`. The generated pod artifact `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_pod/hausdorff_xhd_v25_warm_median_4096.json` aligns with the data presented in the report. The tests in `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py` adequately cover the critical aspects, including adaptive defaults, script metadata, artifact properties, and claim flags, ensuring that the changes behave as expected and that claims are not overstretched. The "Interpretation" section in the report provides a balanced view, clarifying that this is a benchmark quality improvement, not a performance victory, which is further supported by the "Future-Version To-Do List" entry regarding "Exact Hausdorff Device-Resident Nearest-Witness Continuation" in `docs/research/future_version_to_do_list.md`. The explicit "Claim Boundary" in the report and the corresponding `false` flags in the artifact consistently prevent overclaiming.
