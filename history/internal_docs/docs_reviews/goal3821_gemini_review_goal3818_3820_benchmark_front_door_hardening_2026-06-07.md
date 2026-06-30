# Gemini Review: Goals3818-3820 Benchmark Front-Door Hardening

**Date:** 2026-06-07

**Reviewer:** Gemini

## Scope

Review current `main` after:

- `f84b1bae Goal3818 record current benchmark smoke`
- `641e3391 Goal3819 trim report whitespace`
- `f7b19ac6 Goal3820 trim report whitespace`

## Files Inspected

- `docs/reports/goal3818_current_benchmark_contract_smoke_a5000_2026-06-07.md`
- `tests/goal3818_current_benchmark_contract_smoke_a5000_test.py`
- `docs/reports/goal3818_current_benchmark_contract_smoke_a5000/summary.json`
- `docs/reports/goal3818_current_benchmark_contract_smoke_a5000/repair_summary.json`
- `docs/reports/goal3819_triangle_counting_native_mode_probe_2026-06-07.md`
- `tests/goal3819_triangle_counting_native_mode_probe_test.py`
- `docs/reports/goal3819_triangle_counting_native_mode_probe_a5000/triangle_native.stdout.txt`
- `docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_2026-06-07.md`
- `tests/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_test.py`
- `docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_a5000/` (Directory)
- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rtnn/README.md`
- `examples/v2_0/research_benchmarks/triangle_counting/README.md`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
- `examples/v2_0/research_benchmarks/contact_manifold/README.md`

## Questions

1.  **Does Goal3818 fairly record that all ten promoted benchmark apps have at least one current executable A5000 route after the repaired Hausdorff and Contact Manifold commands?**
    *   Answer: Yes, Goal3818 fairly records that all ten promoted benchmark apps have at least one current executable A5000 route. The initial execution shows 8 apps passing directly and 2 apps (`hausdorff_xhd` and `contact_manifold`) failing. Subsequent repairs for these two apps resulted in successful execution, as confirmed by `summary.json`, `repair_summary.json`, and `tests/goal3818_current_benchmark_contract_smoke_a5000_test.py`.
2.  **Are the two initial Goal3818 failures correctly classified as command contract/fail-closed behavior rather than hidden app breakage?**
    *   Answer: Yes, the two initial failures are correctly classified as command contract/fail-closed behavior. The report explicitly states they failed for "expected, fail-closed command-contract reasons." For `hausdorff_xhd`, the failure was due to missing required `--optix-summary-mode directed_threshold_prepared` when `--require-rt-core` was used. For `contact_manifold`, the failure was an intentional fail-closed (`COLLECT_K_BOUNDED overflowed capacity`) due to insufficient `--witness-capacity`. The test `test_fail_closed_messages_are_preserved` confirms these specific error messages, indicating issues with command parameters rather than hidden app breakage.
3.  **Does Goal3819 correctly improve the triangle-counting command guidance by documenting explicit `--optix-graph-mode native` while preserving that the route still does not authorize RT-core triangle-count claims?**
    *   Answer: Yes, Goal3819 correctly improves the triangle-counting command guidance. The `examples/v2_0/research_benchmarks/triangle_counting/README.md` now explicitly recommends `--optix-graph-mode native` for better performance. Crucially, the documentation and the `triangle_native.stdout.txt` report confirm that even with `native` mode, the app still classifies the path as `host_indexed_fallback` and maintains `rt_core_accelerated=false` and `triangle_count_rt_core_claim_authorized=false`, thus correctly preserving the boundary against RT-core claims. This is verified by `tests/goal3819_triangle_counting_native_mode_probe_test.py`.
4.  **Does Goal3820 correctly close the RTNN benchmark-front-door gap by adding a current executable `prepared_optix_ranked_summary` mode that returns pure JSON and wraps the existing generic prepared OptiX ranked-summary aggregate?**
    *   Answer: Yes, Goal3820 correctly closes the RTNN benchmark-front-door gap. The new `--mode prepared_optix_ranked_summary` provides a current executable route, as confirmed by `rtdl_rtnn_benchmark_app.py` and its presence in `--help` output. This mode wraps the existing generic Goal2348 RTNN runner, outputs pure JSON to stdout, and captures runner progress as metadata, which is validated by `test_pod_artifacts_are_pure_json_and_claim_bounded` in `tests/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_test.py` and the content of the generated `stdout.json` artifacts.
5.  **Does the RTNN wrapper remain app-agnostic at the native-engine boundary and avoid hidden partner selection?**
    *   Answer: Yes, the RTNN wrapper remains app-agnostic at the native-engine boundary and avoids hidden partner selection. The report (`docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_2026-06-07.md`) and the `README.md` for RTNN explicitly state that no RTNN-specific native engine vocabulary or ABI changes are introduced, and the engine relies on generic fixed-radius neighbor contracts. The `claim_boundary` definitions within `rtdl_rtnn_benchmark_app.py` and the report also explicitly set `native_engine_customization` and `automatic_partner_selection_authorized` to `False`, confirming this.
6.  **Do the reports/docs avoid release, package-install, public speedup, broad RT-core speedup, paper-reproduction, AMD performance, true-zero-copy, automatic partner selection, and app-specific native-engine claims?**
    *   Answer: Yes, the reports and documentation consistently and explicitly avoid these claims.
        *   `docs/reports/goal3818_current_benchmark_contract_smoke_a5000_2026-06-07.md`, `docs/reports/goal3819_triangle_counting_native_mode_probe_2026-06-07.md`, and `docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_2026-06-07.md` all contain explicit "Boundary" sections that disclaim authorization for release action, package-install wording, public speedup wording, broad RT-core wording (or specific RT-core wording like "triangle-count RT-core wording" or "RTNN paper reproduction wording"), paper reproduction claims, AMD hardware/performance claims, true-zero-copy wording, automatic partner selection, and app-specific native-engine logic.
        *   `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` further reinforces this by explicitly setting flags like `native_engine_customization`, `full_rtnn_paper_reproduction`, `public_speedup_claim_authorized`, `broad_rt_core_speedup_claim_authorized`, `amd_performance_claim_authorized`, `true_zero_copy_claim_authorized`, `release_authorized`, and `automatic_partner_selection_authorized` to `False` within its `CLAIM_BOUNDARY` definitions.
        *   `examples/v2_0/research_benchmarks/triangle_counting/README.md` also clearly states that the `native` mode should be used as internal route evidence, "not as a public RT-core triangle-count claim."

## Verdict

*   Verdict: accept
*   Reasoning: The review confirms that all ten promoted benchmark applications now have at least one executable A5000 route, with initial contract failures for Hausdorff and Contact Manifold being correctly identified and remediated. The triangle-counting documentation has been updated to provide explicit guidance for `--optix-graph-mode native` while strictly maintaining that it does not authorize RT-core claims. The RTNN benchmark front-door gap has been successfully closed with a new, executable `prepared_optix_ranked_summary` mode that returns pure JSON, wraps the existing generic aggregate, and maintains app-agnosticism at the native-engine boundary, avoiding hidden partner selection. Crucially, a consistent and explicit effort is evident across all reviewed reports and documentation to avoid unauthorized claims regarding release, package-install, public speedup, broad RT-core speedup, paper-reproduction, AMD performance, true-zero-copy, automatic partner selection, and app-specific native-engine behavior. The changes are well-documented, tested, and adhere to the project's claim boundaries.
