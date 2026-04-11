# 🟢 RTDL v0.4 Final Release Handoff Hub

**ATTENTION NEXT AI**: Please read this document carefully before taking any further action. It contains the final audit results, environment requirements, and the remaining steps to close the `v0.4.0` release.

---

## 1. Session Mission: Final v0.4 Closure
This handoff is a release-packaging checklist, not the newest source of truth by
itself. A later heavy Linux benchmark exposed, and then a later fix resolved, a
shared accelerated `fixed_radius_neighbors` boundary bug. Use the refreshed
Goal 228/229 evidence before taking any release action.

### Accomplishments:
*   **Audit PASSED**: Full cross-backend parity (CPU, Embree, OptiX, Vulkan) for nearest-neighbor workloads after the fixed-radius boundary repair.
*   **Infrastructure Fix**: Keep the Python 3.9 compatibility note only if the release action is taken from a checkout that still carries that local compatibility patch.
*   **Release Boundary**: This clean release-prep worktree reflects the pushed `main` truth and excludes the unrelated local docs reorganization from the primary checkout.

---

## 2. Technical Evidence & Reports
All work is backed by formal audit artifacts. 

*   **[Final v0.4 Audit Verdict](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/reports/gemini_v0_4_final_re_audit_report_2026-04-10.md)**: technical sign-off and backend parity verification.
*   **[Test Evidence]**: Clean release-prep verification now includes a full `unittest discover` pass with **525 tests, 0 failures, 59 skips**, plus CLI/artifact/Embree smokes via `scripts/run_full_verification.py`.
*   **[Support Matrix](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/support_matrix.md)**: Honestly updated for "reopened for GPU" status.
*   **[Heavy Linux Benchmark](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_2026-04-10.md)**: refreshed heavy nearest-neighbor benchmark and parity evidence.
*   **[Boundary Fix Follow-Up](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/reports/goal229_fixed_radius_neighbors_accelerated_boundary_fix_2026-04-10.md)**: exact repair rationale, regression tests, and Linux rerun proof.
*   **[Final Pre-Release Verification](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/reports/goal232_final_pre_release_verification_2026-04-10.md)**: clean-worktree verification transcript and release-decision package.

---

## 3. Critical Environment Requirements
The release-prep worktree should be treated as the canonical packaging checkout.

> [!CAUTION]
> Do not assume local-only compatibility or docs-reorganization changes from the
> primary checkout are present here unless they have been deliberately
> reintroduced and reviewed.

---

## 4. Visual & Content Assets
*   📚 **Bibliography**: Consolidated the research paper list into the [Foundations Document](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/workloads_and_research_foundations.md).
*   🏠 **Main Entry**: Current committed front page is at [README.md](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/README.md).
*   📂 **Docs Hub**: Current committed documentation index is at [docs/README.md](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/README.md).

---

## 5. 🛠 Remaining Release Actions
The code and documentation are close, but release packaging should still wait
for the refreshed heavy benchmark evidence and the boundary-fix slice to be the
accepted current truth. After that, the next AI should execute the following:

1.  **Use the clean release-prep worktree** rather than the unrelated dirty primary checkout.
2.  **Stage only the deliberate final release package changes**.
3.  **Final Commit**: use a bounded release-packaging commit message, not a catch-all commit over unrelated local dirt.
4.  **Version Update**: Increment the [VERSION](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/VERSION) file from `v0.3.0` to `v0.4.0` only after explicit user authorization.
5.  **Git Tag**: Create the official `v0.4.0` tag only after explicit user authorization.

---
*Status: Packaging checklist only. Verify refreshed Goal 228/229 evidence before any v0.4.0 release action.*
