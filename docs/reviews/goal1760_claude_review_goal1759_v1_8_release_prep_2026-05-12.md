# Goal1760 Claude Review: Goal1759 v1.8 Release Prep After Legacy Native Cleanup

**Date:** 2026-05-12
**Reviewer:** Claude (independent)
**Verdict:** `accept-with-boundary`

## Scope

This review covers the full Goal1758 → Goal1759 release-prep chain, including the updated Goal1742 evidence packet, Goal1750 same-contract performance summary, Goal1753 decision-status note, Goal1754 commit-ready inventory, and the associated test suite for each goal. The review does not authorize a tag, version bump, push, or package release.

---

## Question 1 — Does Goal1758 correctly remove the known multi-backend source/ABI blocker?

**Finding: Yes, within validated scope.**

Goal1758 renames 14 old app-shaped native support symbols across Apple RT, HIPRT, Oracle, and Vulkan from the `lsi` / `overlay` / `triangle_probe` family to generic names (`rtdl_*_run_segment_pair_intersection`, `rtdl_*_run_shape_pair_relation_flags`, `rtdl_*_run_triangle_cycle_candidates`). The internal native vocabulary (`RtdlLsiRow`, `GpuLsiRecord`, `LsiQueryState`, and equivalents) was also migrated.

The post-cleanup source scan over `src/native/**` reports:

- Old lower-case native ABI hits for `lsi`, `overlay`, `triangle_probe`: **0**
- Old source vocabulary hits for `Lsi`, `Overlay`, `LSI`, `triangle_probe`: **0**
- Replacement generic symbols present: **confirmed across all four backends**

Validation steps recorded: `py_compile` for all touched Python runtime files; focused native leakage gate covering `goal1603`, `goal1668`, `goal1676`, `goal1680`, `goal1704`, and `goal1708` tests; local Linux `make build-embree` on `192.168.1.20` reporting Embree 4.3.0.

The `goal1758_legacy_lsi_overlay_triangle_probe_native_cleanup_test.py` test directly asserts every old symbol absent from native and runtime source trees and every new symbol present. The test also asserts old vocabulary absent via regex covering `\blsi\b`, `\boverlay\b`, `triangle_probe`, `\bLsi\b`, `\bOverlay\b`, `\bLSI\b`.

The stated boundary is correct: this is source, Python-binding, scan, and Embree build evidence. It is not pod or hardware evidence for HIPRT, Vulkan, Apple RT, or OptiX. Those remain platform-specific evidence items and the report does not convert them into a universal backend support claim. That is the appropriate boundary.

---

## Question 2 — Do Goal1742, Goal1753, Goal1754, and Goal1759 preserve conservative release boundaries after the cleanup?

**Finding: Yes.**

**Goal1742** declares `v1_8_release_candidate_packet_ready_for_external_review` and explicitly states it does not authorize a tag, version bump, package upload, or public release. The source-tree-only install boundary is documented; the test confirms `pyproject.toml`, `setup.py`, and `setup.cfg` are all absent. `VERSION` reads `v1.5` — unchanged. The partner direction (v2.0 milestone) remains separated from the v1.8 scope.

**Goal1753** declares `v1_8_decision_status_ready_except_claude_review_and_user_release_authorization`. It explicitly records the earlier Claude review attempt as a non-event (the attempt failed with a usage-limit error; the intended output file `goal1752_claude_review_updated_goal1742_1750_v1_8_packet_2026-05-12.md` is confirmed absent). The test asserts `VERSION` remains `v1.5`.

**Goal1754** declares `v1_8_inventory_ready_with_external_review_blocker`. It lists all v1.8 decision-trail files, the performance clarification chain, and the handoff files. It explicitly prohibits claiming the missing Claude review exists. The focused gate is recorded as passing (`Ran 167 tests in 4.617s; OK (skipped=1)`). Protected local files are identified with a do-not-stage list.

**Goal1759** declares `v1_8_release_prep_ready_for_fresh_external_review` and lists five pre-release blockers (fresh Claude review, fresh Gemini review, gate re-run, final consensus note, explicit user authorization). This is correctly structured.

All four reports consistently carry the release boundary and none attempt to advance beyond it unilaterally.

---

## Question 3 — Are public overclaims still blocked?

**Finding: All specified overclaims remain blocked across the chain.**

The following overclaims are explicitly blocked in Goal1742 and Goal1759, and the corresponding tests assert their presence in the blocked-wording sections:

| Overclaim | Status |
| --- | --- |
| Package-install support | Blocked; no packaging metadata files exist; test confirms |
| Broad speedup / `--backend optix` proves a public speedup | Blocked |
| Whole-application acceleration | Blocked |
| Universal backend support | Blocked; hardware validation acknowledged as platform-specific only |
| Python+partner+RTDL shipped at v1.8 | Blocked; v2.0 milestone, not v1.8 |
| Universal PyTorch/CuPy support | Blocked |
| True zero-copy support | Blocked |
| Recovered v1.0 Embree app-level rows as public same-contract speedup evidence | Blocked |

Goal1750 performance data is correctly scoped: OptiX has 17 same-contract primary ratio rows and Embree has 1 strict same-contract database row, with the remaining 14 recovered app-level rows classified as `phase_mapped_diagnostic` (4), `timing_schema_mismatch` (7), or `missing_current_artifact` (3). The summary verdict `same_contract_perf_summary_ready_without_public_claim` is correct and the `public_claim_authorized` and `release_authorized` flags are both `false` per the JSON output.

---

## Question 4 — Is v1.8 now ready for a final consensus note?

**Finding: Conditionally yes — this review satisfies the Claude review requirement. Three blockers remain.**

The remaining procedural blockers identified in Goal1759 are:

1. **Fresh Gemini review** of the updated Goal1742 / Goal1750 / Goal1758 / Goal1759 chain — not yet present.
2. **Focused v1.8 gate re-run** after review files land — should be confirmed after this review and the Gemini review are committed.
3. **Final v1.8 consensus/decision note** contingent on Codex, Claude, and Gemini agreement.
4. **Explicit user authorization** before any `VERSION` bump, tag, push, or release operation.

This Claude review satisfies blocker (1) for the Claude side. If Gemini also returns `accept` or `accept-with-boundary` on the same chain, and the gate re-run passes with no new failures, the project is positioned to write a final consensus note. That note must still precede any release action, and release action requires explicit user authorization — neither of which is provided here.

---

## Summary

The Goal1758 cleanup is technically sound within its stated validation scope. The four surrounding goals (1742, 1753, 1754, 1759) preserve conservative release boundaries without exception. All six specified overclaim families remain blocked with both document-level wording and test-level assertions. The chain is internally consistent.

**Verdict: `accept-with-boundary`**

The boundary: this review does not authorize release, tag, version bump, package upload, or push. A final consensus note requires a matching Gemini review, a gate re-run, and explicit user authorization for any release operation.
