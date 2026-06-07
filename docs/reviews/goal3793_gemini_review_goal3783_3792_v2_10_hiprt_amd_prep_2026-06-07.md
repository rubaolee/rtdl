# Independent Gemini Review: Goal3783-3792 v2.10 HIPRT/AMD Prep

**Date:** 2026-06-07

**Verdict:** accept

## Executive Summary

The `Goal3783-3792` chain successfully establishes the foundational HIPRT parity and AMD functional validation framework without prematurely claiming AMD hardware capabilities. All specified reports, scripts, and tests demonstrate adherence to a fail-closed methodology, clearly distinguishing between NVIDIA control evidence and actual AMD hardware results. The review confirms that the work performed sets up the next crucial step: executing the defined functional validation on an actual AMD pod. The chain consistently upholds architectural boundaries, avoiding overclaims related to performance, release, or specific hardware/software features.

## Verification Points

1.  **Goal3783 correctly records NVIDIA CUDA/Orochi HIPRT parity closeout evidence without presenting it as AMD hardware evidence.**
    *   **Status:** Verified. `docs/reports/goal3783_v2_10_hiprt_parity_closeout_packet_2026-06-07.md` explicitly states that the validation is on the NVIDIA CUDA/Orochi HIPRT route and "is not AMD hardware evidence and does not authorize AMD performance wording." It clearly lists the NVIDIA A5000 GPU used for validation.

2.  **Goal3784 defines a fail-closed AMD functional validation gate requiring actual AMD hardware, all ten benchmark apps ready/pass, clean source, parity acceptance, and all claim flags false.**
    *   **Status:** Verified. `docs/reports/goal3784_amd_hiprt_functional_validation_runbook_2026-06-07.md` outlines a strict set of criteria for AMD Pod Acceptance, including `hardware_vendor: amd`, `focused_tests_passed: true` for all ten apps, `scoped_source_dirty: false`, `parity_validation.status: accept`, and all claim-boundary flags remaining `false`. The runbook explicitly rejects NVIDIA evidence.

3.  **Goal3785's pod runner rejects non-AMD hardware and writes a bounded control artifact instead of silently treating NVIDIA HIPRT/Orochi as AMD evidence.**
    *   **Status:** Verified. `docs/reports/goal3785_amd_hiprt_functional_pod_runner_2026-06-07.md` details the fail-closed nature of `scripts/goal3785_amd_hiprt_functional_pod_runner.py`. On non-AMD hardware, it generates a `non_amd_hiprt_functional_runner_control.json` artifact with `status: reject_non_amd_hardware` and explicitly states this output is not AMD hardware evidence.

4.  **Goal3786 correctly refreshes benchmark adequacy: ten ready apps, zero Numba-reference gaps, zero AMD performance authorization, and no release authorization.**
    *   **Status:** Verified. `docs/reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md` presents a matrix showing all 10 benchmark apps as "adequate" or "strong" and "ready for AMD functional pod; Goal3784 artifact pending". It confirms that no app is awaiting a Numba reference and explicitly states that it "does not authorize AMD performance claims" or "release action."

5.  **Goal3787's combined A5000 regression packet is internally consistent and does not overclaim beyond NVIDIA CUDA/Orochi HIPRT control evidence.**
    *   **Status:** Verified. `docs/reports/goal3787_post_hiprt_closeout_regression_packet_2026-06-07.md` consolidates validation from multiple prior goals, all performed on NVIDIA RTX A5000. The artifact records `HIPRT parity validation: accept`, `benchmark adequacy validation: accept`, `Numba reference gaps: none`, and `all claim-boundary flags: false`. It explicitly labels this as "NVIDIA CUDA/Orochi HIPRT regression evidence: not AMD hardware evidence."

6.  **Goal3788 correctly closes the stale Hausdorff generic-adapter TODO and proves the generic alias plus executed-ops metadata are already repaired.**
    *   **Status:** Verified. `docs/reports/goal3788_hausdorff_generic_alias_and_metadata_audit_2026-06-07.md` confirms the closure of a stale planning note regarding Hausdorff generic naming. It verifies that the generic front door `directed_max_of_nearest_distance_2d_partner_columns` is in use, and the Numba metadata correctly reports `v2_8_partner_continuation_operations_semantics: executed_operations_this_call`.

7.  **Goal3790 makes HIPRT SDK prefix discovery robust enough for future AMD pods: explicit overrides still work, version-suffixed SDK directories are auto-discovered, archive matches are ignored, the chosen prefix is recorded, and the non-AMD control path remains rejected.**
    *   **Status:** Verified. `docs/reports/goal3790_amd_hiprt_runner_prefix_discovery_2026-06-07.md` details the enhancements to `scripts/goal3785_amd_hiprt_functional_pod_runner.py`, explicitly mentioning auto-discovery, ignoring archives, respecting overrides, recording resolution, and maintaining the fail-closed behavior for non-AMD paths.

8.  **Goal3792 records the current post-discovery A5000 control regression at commit `a7a10228`: 34 modules, 185 tests, scoped source clean, parity and adequacy accepted, and all claim-boundary flags false.**
    *   **Status:** Verified. `docs/reports/goal3792_post_runner_discovery_regression_packet_2026-06-07.md` confirms these specifics, detailing the execution on NVIDIA RTX A5000 at commit `a7a10228`, with 34 test modules, 185 tests run successfully, `scoped source dirty: false`, and all internal validation flags indicating `accept` or `false` for claim boundaries.

9.  **The chain preserves the app-agnostic engine boundary and avoids automatic partner-selection, true-zero-copy, broad RT-core, paper-reproduction, and public release claims.**
    *   **Status:** Verified. All reviewed reports include explicit "Boundary" sections that consistently disclaim authorization for AMD performance claims, public speedup wording, whole-app acceleration, broad RT-core wording, paper-reproduction, release claims, zero-copy claims, or app-specific native-engine logic. This demonstrates consistent adherence to the defined scope and boundaries.

## Known Boundaries & Next Steps

This review acknowledges the known boundaries as outlined in the request:
- There is no actual AMD GPU evidence yet.
- The A5000 pod evidence serves solely as implementation/control evidence.
- The next hardware step remains the execution of the Goal3785 runner on an AMD pod, which will produce `docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`.
- This handoff does not authorize v2.10 release or public performance wording.

The work completed provides a robust and auditable foundation for proceeding with actual AMD hardware validation.
