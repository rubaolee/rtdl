# Goal3914 Gemini Review: Goal3912/3913 RayJoin Propagation and Runbook

Date: 2026-06-08

Reviewer: Gemini 2.5 Flash via Gemini CLI, independent external review.

## Review Questions and Answers

### 1. Does Goal3912 correctly propagate nested subprobe timing and loaded-case route metadata into the representative RayJoin profile without changing benchmark semantics?

**Answer:** Yes. The `_case_summary` function in `scripts/goal3866_rayjoin_representative_scale_profile.py` has been updated to correctly extract and include `rtdl_optix_execution_route`, `loaded_case_reuse_enabled`, and `subprobe_wrapper_phase_timing_sec` from the raw probe data into the higher-level representative profile summary. The unit test `tests/goal3912_rayjoin_representative_subprobe_timing_propagation_test.py` explicitly validates this propagation logic, ensuring that the relevant fields are present when expected and that the function handles older data gracefully. The accompanying report `docs/reports/goal3912_rayjoin_representative_subprobe_timing_propagation_2026-06-08.md` further confirms that this change is strictly for artifact propagation and does not alter benchmark semantics, native RTDL behavior, partner code, or existing claim authorizations.

### 2. Does Goal3913 provide a materially safer next-pod runbook, especially against Windows PowerShell local interpolation of remote `$(...)`/`$var` expressions?

**Answer:** Yes. The `docs/handoff/GOAL3913_SAFE_NEXT_POD_RAYJOIN_RUNBOOK_2026-06-08.md` provides a materially safer runbook. It specifically addresses the risks associated with Windows PowerShell's local interpolation of remote expressions by recommending that remote shell variables and `$(...)` expansions be kept out of PowerShell double-quoted strings. Instead, it instructs users to pipe a full bash script to SSH via stdin. Crucially, it includes explicit safety guards like using `mktemp -d` for workspace creation and includes an assertion `test "$workdir" != "/root"` to prevent accidental deletion of the root directory. The `tests/goal3913_safe_next_pod_rayjoin_runbook_test.py` verifies the presence of these essential safety mechanisms within the runbook.

### 3. Do both goals preserve the app-agnostic engine boundary and avoid new speedup/release/RayJoin-reproduction/zero-copy claims?

**Answer:** Yes. Both Goal3912 and Goal3913 consistently preserve the app-agnostic engine boundary and explicitly avoid new claims.
*   **Goal3912:** The change is purely for diagnostic data propagation within the existing benchmark framework. Its report (`docs/reports/goal3912_rayjoin_representative_subprobe_timing_propagation_2026-06-08.md`) explicitly states that it does not change RayJoin semantics, native RTDL, partner code, dispatch policy, or claim authorization. The `_claim_boundary` mechanism within `scripts/goal3866_rayjoin_representative_scale_profile.py` also reinforces these restrictions.
*   **Goal3913:** The runbook's purpose is operational safety and evidence collection for diagnostic purposes. Its "Expected Evidence" section clearly states that it "does not authorize release, RayJoin reproduction, broad RT-core speedup, whole-app speedup, or true-zero-copy claims."
Both goals focus on improving observability and operational robustness without introducing new functional behavior to the engine or making any unauthorized performance claims. This aligns with the findings of the Goal3911 external review regarding the underlying changes in Goal3909/3910.

### 4. Are the local tests sufficient for these non-hardware changes, and what must still be proven on a fresh A5000 pod?

**Answer:** The local unit tests (`tests/goal3912_rayjoin_representative_subprobe_timing_propagation_test.py` and `tests/goal3913_safe_next_pod_rayjoin_runbook_test.py`) are sufficient for verifying the logical correctness of data propagation and the presence of critical safety instructions within the runbook, respectively. Since these goals involve non-hardware changes (data structuring and procedural instructions), detailed local testing is appropriate for their intended scope.

What must still be proven on a fresh A5000 pod is the successful end-to-end execution of the runbook itself. This includes verifying:
*   The remote execution environment is correctly set up and the bash script runs to completion without errors.
*   The generated `summary.json` artifact contains all the "Expected Evidence" detailed in the Goal3913 runbook, specifically the `wrapper_phase_timing_sec`, `cases[*].subprobe_wrapper_phase_timing_sec`, `cases[*].loaded_case_reuse_enabled: true`, and execution routes suffixed with `_loaded_case_reuse` for LSI and overlay cases.
*   The collected timing data, while not part of this review's quantitative analysis, is present and appears to be well-formed, indicating successful instrumentation.

The A5000 run will serve as an integration and smoke test for the entire diagnostic data collection process, confirming that the implemented changes function as expected in a real-world, production-like environment.

## Verdict

**Verdict:** `accept`

## Tests Run

No tests were run as part of this read-only external review.
