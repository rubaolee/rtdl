# RTDL v0.4 Final Release Handoff Hub

Archived release handoff.

This document is preserved as the historical release-packaging hub used before `v0.4.0` publication. It is not the live source of truth for the already-released repository state.

Current source of truth:

- [README.md](../../../README.md)
- [docs/README.md](../../README.md)
- [docs/release_reports/v0_4/release_statement.md](../../release_reports/v0_4/release_statement.md)
- [docs/handoff/V0_4_FINAL_RELEASE_SIGN_OFF_SUMMARY_2026-04-11.md](../../handoff/V0_4_FINAL_RELEASE_SIGN_OFF_SUMMARY_2026-04-11.md)

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

*   **[Final v0.4 Audit Verdict](../../reports/gemini_v0_4_final_re_audit_report_2026-04-10.md)**: technical sign-off and backend parity verification.
*   **[Test Evidence]**: Clean release-prep verification now includes a full `unittest discover` pass with **525 tests, 0 failures, 59 skips**, plus CLI/artifact/Embree smokes via `scripts/run_full_verification.py`.
*   **[Support Matrix](../../release_reports/v0_4/support_matrix.md)**: Honestly updated for "reopened for GPU" status.
*   **[Heavy Linux Benchmark](../../reports/goal228_v0_4_heavy_nearest_neighbor_perf_2026-04-10.md)**: refreshed heavy nearest-neighbor benchmark and parity evidence.
*   **[Boundary Fix Follow-Up](../../reports/goal229_fixed_radius_neighbors_accelerated_boundary_fix_2026-04-10.md)**: exact repair rationale, regression tests, and Linux rerun proof.
*   **[Final Pre-Release Verification](../../reports/goal232_final_pre_release_verification_2026-04-10.md)**: clean-worktree verification transcript and release-decision package.

---

## 3. Critical Environment Requirements
The release-prep worktree should be treated as the canonical packaging checkout.

> [!CAUTION]
> Do not assume local-only compatibility or docs-reorganization changes from the
> primary checkout are present here unless they have been deliberately
> reintroduced and reviewed.

---

## 4. Visual & Content Assets
*   📚 **Bibliography**: Consolidated the research paper list into the [Foundations Document](../../workloads_and_research_foundations.md).
*   🏠 **Main Entry**: Current committed front page is at [README.md](../../../README.md).
*   📂 **Docs Hub**: Current committed documentation index is at [docs/README.md](../../README.md).

---

## 5. Historical Meaning

This handoff records the release-packaging checklist that existed before the `v0.4.0` tag and `main` publication. Those actions are already complete in the released repository history.

Use this file for process reconstruction only, not for new release instructions.

---
*Status: historical packaging checklist. `v0.4.0` has already been released.*
