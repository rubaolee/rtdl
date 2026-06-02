Date: 2026-06-01

## Gemini Review for Goal2995 RayDB Numba Min/Max

**Verdict: `accept`**

### Findings

The independent review confirms the internal consistency of the Goal2995 implementation, documentation, and reported L4 pod evidence. All questions posed in the prompt have been addressed and validated through static analysis of the provided artifacts.

**Limitation:** Due to an inability to execute shell commands within this environment, the live execution and verification of the provided test command (`PYTHONPATH=src:. python -m unittest tests.goal2995_raydb_numba_minmax_l4_pod_test tests.goal2995_raydb_numba_segmented_minmax_test tests.goal2994_raydb_numba_neutral_demo_test`) could not be performed by this agent. The assessment of runtime conformance relies entirely on the provided `docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json` artifact and `docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.md` report.

### Answers To Questions

1.  **Do the new `segmented_min_f64` and `segmented_max_f64` Numba operations remain generic grouped reductions, without RayDB/app-specific engine logic?**
    *   **Yes.** The `describe_numba_segmented_min_f64` and `describe_numba_segmented_max_f64` descriptors confirm generic `input_columns` (`group_ids:int64`, `values:float64`) and generic `empty_group_fill` (`initial`). The `numba_partner_continuation.py` code, as verified by `tests/goal2995_raydb_numba_segmented_minmax_test.py`, explicitly avoids "raydb" terms, affirming that these are generic grouped reductions. The `docs/reports/goal2995_raydb_numba_segmented_minmax_prepared_2026-06-01.md` also states their generic nature, unrelated to RayDB-specific engine functions.

2.  **Does the `partner="numba"` front door still require accepted v2.6 neutral handoff before launching Numba, and does it avoid torch carrier/conversion?**
    *   **Yes.** The `run_raydb_v2_6_numba_neutral_continuation_preview` function in `rtdl_raydb_style_benchmark_app.py` clearly uses `rt.prepare_v2_6_neutral_partner_handoff` and `rt.validate_v2_6_neutral_partner_handoff`. The test `test_partner_minmax_front_doors_accept_numba_branch_and_reject_host_columns` confirms that host columns are rejected without this handoff. Furthermore, the metadata in the `run_raydb_v2_6_numba_neutral_continuation_preview` function and the L4 pod report/artifact explicitly set `uses_legacy_torch_carrier: false` and `uses_torch_conversion: false`.

3.  **Does the RayDB-style app now correctly support all five scalar modes using user-selected Numba while keeping query encoding in app Python?**
    *   **Yes.** The `docs/reports/goal2995_raydb_numba_segmented_minmax_prepared_2026-06-01.md` and `tests/goal2995_raydb_numba_segmented_minmax_test.py` confirm support for `count`, `sum`, `min`, `max`, and `avg_as_sum_count`. The L4 pod artifact shows `match_cpu: true` for all five modes. The `app_owned_lowering` field in `describe_raydb_v2_6_numba_neutral_continuation` and in the prepared report explicitly states that RayDB query encoding remains in app Python.

4.  **Is the L4 pod evidence valid runtime conformance evidence for those modes? Please check rows/groups, source commit, toolchain metadata, CPU parity, and claim-boundary fields.**
    *   **Yes, the L4 pod evidence is valid runtime conformance evidence.**
        *   **Rows/Groups:** The JSON artifact (`docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json`) and the markdown report (`docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.md`) consistently report `rows: 1,000,000` and `groups: 4,096`.
        *   **Source Commit:** The `source_commit` is `b41369e4b4becb3534e729658db41642c643abe2` in both documents.
        *   **Toolchain Metadata:** Comprehensive toolchain details (Python, NumPy, Numba, CUDA versions, and environment variables) are present in the JSON artifact and summarized in the markdown report.
        *   **CPU Parity:** All five modes show `match_cpu: true` in the JSON artifact and the report explicitly states "All five modes matched the CPU NumPy reference," with `max_abs_error` values provided for sum and avg_as_sum_count.
        *   **Claim-Boundary Fields:** Both the JSON artifact and the markdown report include explicit `claim_boundary` sections, setting all authorization flags (e.g., `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`) to `false`.

5.  **Are the roadmap/readiness updates honest, especially the point that Goal2995 is not release evidence or speedup evidence?**
    *   **Yes, the roadmap/readiness updates are honest.** Both `src/rtdsl/v2_6_roadmap.py` and `src/rtdsl/v2_5_internal_readiness.py` consistently and explicitly frame Goal2995 as "conformance_passed_not_speedup_evidence" or similar. The `validate_v2_6_roadmap` function includes checks to ensure Goal2995 is not treated as speedup evidence, and `v2_5_internal_readiness_packet` lists Goal2995 as an action item for external review, reinforcing its status as a step in a larger development process rather than a final release or speedup authorization.

### Residual Boundaries

*   This goal does not authorize v2.6 release, public speedup claims, whole-app speedup claims, broad RT-core speedup claims, true zero-copy claims, Numba speedup claims, RayDB paper reproduction claims, or automatic partner selection claims.
*   The review performed by this agent relies solely on the provided pre-generated L4 pod evidence and static code/documentation analysis. Live validation of the runtime conformance tests could not be performed.
