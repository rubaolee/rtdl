This is an independent Gemini/Antigravity review of Goal1914, distinct from Codex.

**Verdict:** accept

**Review of Goal1914 - v2 Pod Artifact Provenance Hardening**

**Scope:** Review the local changes that harden v2.0 pod artifact provenance, specifically:
- `scripts/goal1878_fixed_radius_app_adapter_perf.py`
- `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`
- `scripts/goal1903_v2_partner_pod_batch_runner.sh`
- `scripts/goal1905_v2_partner_pod_batch_acceptance.py`
- `docs/reports/goal1905_v2_partner_pod_batch_acceptance_2026-05-13.md`
- `docs/reports/goal1914_v2_pod_artifact_provenance_hardening_2026-05-13.md`
- `tests/goal1914_v2_pod_artifact_provenance_hardening_test.py`
- the Goal1908 / Goal1911 / Goal1899 integration points.

**Analysis:**

1.  **Does the hardening correctly make accepted Goal1903 / Goal1905 artifacts fail closed when RTX GPU provenance, git commit, or matching `source_commit_label` is missing?**
    *   **Yes.** The performance scripts (`goal1878`, `goal1863`) now explicitly output `git_commit`, `source_commit_label`, and `gpu` information. The `goal1903` batch runner script includes embedded Python logic that performs strict checks for the presence of "RTX" in the GPU field, a valid `git_commit`, and a matching `source_commit_label`, raising a `SystemExit` if any condition is not met. Similarly, the `goal1905` acceptance script's `_validate_pod_provenance` function enforces these checks, adding errors that lead to a "fail" status. This multi-layered validation ensures a robust fail-closed mechanism for provenance.

2.  **Does it preserve the current claim boundary: no v2.0 release authorization, no broad RT-core speedup claim, and no whole-app speedup claim?**
    *   **Yes.** All reviewed scripts (`goal1878`, `goal1863`, `goal1903`, `goal1905`) explicitly set `"v2_0_release_authorized": False`, `"whole_app_speedup_claim_authorized": False`, and `"broad_rt_core_speedup_claim_authorized": False` within their respective `claim_boundaries` or `claim_boundary` sections. Furthermore, both `goal1903` and `goal1905` contain logic (`_check_boundary_false` and `_check_forbidden_claims` functions) that actively verifies these claims remain `False`, causing a failure if they are unexpectedly `True`. The boundaries are well-preserved.

3.  **Are there any obvious stale-artifact or mixed-source holes still open before the next RTX pod run?**
    *   **No obvious holes.** The stringent checks for `git_commit`, `source_commit_label`, and RTX GPU provenance implemented at both the batch execution and acceptance validation stages directly mitigate the risk of stale or mixed-source artifacts. The `goal1903` runner's method of deriving `SOURCE_COMMIT_LABEL` from `git rev-parse HEAD` by default, combined with the subsequent checks, provides good protection against unintentional source mismatches. The `--allow-missing` flag in `goal1905` for pre-pod snapshots, which warns about stale summary requests, further demonstrates awareness and handling of potential staleness.

4.  **Is the local validation (`Goal1908` preflight pass) enough for pre-pod readiness, while still requiring actual pod artifacts and post-pod review?**
    *   **Yes, this is correctly handled.** The `docs/reports/goal1914_v2_pod_artifact_provenance_hardening_2026-05-13.md` explicitly states that `Goal1908` "remains a non-pod preflight" and that its readiness snapshot "still correctly reports v2.0 as blocked on missing RTX pod artifacts and final reviews." The use of `--allow-missing` when `goal1908` runs `goal1905` confirms that it's an early, permissive check. The requirement for actual pod artifacts, strict `goal1905` validation, and external review for final release authorization is clearly documented and enforced by the system design.

**Conclusion:**
The Goal1914 provenance hardening effectively closes critical gaps, ensuring that only verified and appropriately sourced RTX pod artifacts can proceed through the pipeline. The implementation is robust, aligns with the stated goals, and maintains necessary claim boundaries. The role of local preflight validation versus actual pod artifact validation is clearly delineated. This is a well-engineered hardening step.
