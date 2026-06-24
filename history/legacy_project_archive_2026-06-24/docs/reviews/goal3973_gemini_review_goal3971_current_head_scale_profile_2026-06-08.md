## Independent Gemini Review for Goal3971 Current-Head Scale Profile

**Date:** 2026-06-08

**Reviewer:** Gemini

---

### Verdict

**accept-with-boundary**

The Goal3971 scale-profile packet provides valid evidence that all 10 benchmark rows pass under the documented partner setup on the RTX 4000 Ada, and correctly explains the partner-toolchain resolution. The evidence carefully avoids overclaiming. However, the current setup is presented as a one-off evidence packet rather than a fully reusable runbook.

---

### Questions Answered

1.  **Is the Goal3971 RTX 4000 Ada current-head scale-profile packet valid evidence that all 10 benchmark rows pass under the documented partner setup?**
    *   **Answer**: Yes. The `summary.json` (specifically `"all_pass": true` and `"json_pass_count": 10`) and the `final_partner_complete_rerun.log` confirm that all 10 benchmark rows passed successfully after applying the documented partner setup. The included unit tests further validate these assertions.

2.  **Does the report correctly explain the partner-toolchain issue: missing Numba, then Numba PTX 8.7 versus driver PTX 8.4, then the working CUDA 12.4 compiler-package pin plus CuPy?**
    *   **Answer**: Yes. The "Partner Toolchain Setup Lesson" section in `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08.md` accurately details the encountered issues (missing Numba, then PTX version mismatch) and their resolution (Numba 0.60.0, CUDA 12.4 compiler package pin via `nvidia-cuda-nvcc-cu12==12.4.131`, and CuPy 14.1.1). The provided log files (`numba_missing_then_ptx87_mismatch.log`, `numba_cuda124_fix_rerun.log`, `final_partner_complete_rerun.log`) corroborate this explanation.

3.  **Does the evidence avoid overclaiming release, public speedup, broad RT-core, whole-app acceleration, true-zero-copy, AMD performance, package install, paper reproduction, automatic partner selection, or app-specific native engine logic?**
    *   **Answer**: Yes. The "Boundary" section in the main report and the corresponding `false` flags in `summary.json` explicitly disclaim all the mentioned aspects. The test suite includes checks (`test_claim_boundaries_remain_false`) to ensure these boundaries are maintained and not overclaimed.

4.  **Are the Goal3971 tests sufficient to guard the artifact and setup lesson?**
    *   **Answer**: Yes. The `tests/goal3971_current_head_scale_profile_after_loader_closeout_test.py` file contains comprehensive unit tests that verify the summary, clean working tree, GPU, passing status of all benchmarks (including specific partner rows), correct Numba/CuPy versions in the logs, explicit boundary statements in the report, existence of output files, and clean stderr. This provides strong assurance for the validity of the artifact and the setup lesson.

5.  **What should be required before treating this setup as a reusable pod runbook rather than a one-off evidence packet?**
    *   **Answer**: To elevate this setup from a one-off evidence packet to a reusable pod runbook, the following would be required:
        *   **Full automation of the setup process**: Codify all manual steps (dependency installation, version pinning, environment variable settings) into robust, idempotent scripts.
        *   **Validation of the automation**: Thoroughly test the automated setup to ensure consistent and reliable environment reproduction across different pod instances.
        *   **Comprehensive documentation**: Create clear, actionable runbook documentation covering usage, expected inputs, and outputs.
        *   **Parameterization/Generalization**: Abstract any pod-specific configurations or versions to allow for broader applicability and maintainability.
        *   **Version control and CI/CD integration**: Integrate the runbook into version control and potentially a CI/CD pipeline for continuous validation and deployment.
        *   **Expanded monitoring**: Implement continuous monitoring for environmental drift or failures when using the runbook in a production-like context.
