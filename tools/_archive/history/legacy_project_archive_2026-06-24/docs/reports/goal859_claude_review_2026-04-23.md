**Verdict: Approved.**

Key reasons:

1. **Contract fidelity.** All six profiler functions (`_profile_service_{cpu,embree,scipy}`, `_profile_event_{cpu,embree,scipy}`) produce artifacts using the four canonical Goal835 phase names (`input_build`, `optix_prepare`, `optix_query`, `python_postprocess`). The mapping table at line 352–358 correctly binds each app/backend pair to its `path_name` and `baseline_name`.

2. **Correct parity checks.** CPU and SciPy service paths compare against `cpu_python_reference` via `run_case`; Embree paths compare against `embree gap_summary/count_summary`. Event paths follow the same pattern. No cross-semantic comparison leak.

3. **Summary extraction is semantically tight.** `_service_summary_from_count_rows` correctly filters on `threshold_reached != 0` (line 62). `_event_summary_from_count_rows` reads pre-aggregated `neighbor_count` directly (line 100). Neither inflates or deflates coverage/hotspot counts.

4. **Tests are adequate for the scope.** Five tests cover: service-CPU contract fields, event-Embree contract fields, CLI round-trip + stdout JSON, SciPy mock-isolated parity path, and guard-clause rejections. The mock-based SciPy test (test 4) correctly patches at the module level.

5. **Boundary is clean.** The script makes no RTX claim, no whole-app row-vs-summary timing comparison, and no promotion action — consistent with the stated scope.

One minor note: `_time_call` captures `case` in a closure for `_run_rows` calls (e.g. lines 123, 202), which is fine here since `case` is stable across iterations. No correctness issue.
