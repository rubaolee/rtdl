I have all five amended files. Checking each finding against the amendments:

---

## Finding-by-Finding Closure Check

### P0-A — Test matrix count discrepancy in blocker ledger

**CLOSED.**

The amended `v3_release_authorization_blockers_2026-06-20.md` now correctly separates the "Evidence And Gates" section into two labeled subsections:

- **"Historical scoped-surface validation before Phase H/G"** — retains the original `106 modules / 509 tests OK` without deleting or conflating it.
- **"Current Phase H/G validation"** — records the new `module_count: 148, tests: 754, status: OK`.

The ledger then adds the required explanation: *"The matrix count increased from the earlier 106 modules / 509 tests because the Phoenix rebuild line added Phase H/G front-door, source-tree-doctor, capability branch, and later Phoenix V3 route/gate tests. The current authoritative local matrix result is 148 modules / 754 tests OK."*

Both the discrepancy and its cause are now fully resolved.

---

### P0-B — Gate clarity: readiness test pass vs. readiness gate redo_required

**CLOSED.**

The amended candidate (`phoenix_v3_phase_h_g_capability_completion_candidate_2026-06-24.md`) adds the required clarifying sentence immediately after the 19-test result:

> "The `v3_phoenix_release_readiness_gate_test` passing means the gate correctly reports the current high-performance branch as `redo_required`; it is expected behavior, not release authorization."

This is substantively identical to the parenthetical I required and eliminates the apparent contradiction for any reader who did not know the test suite's internal structure.

---

### P1-A — Documentation map audience segregation

**CLOSED.**

The amended `docs/public_documentation_map.md` now opens the table with:

> "Rows labeled `V3 rebuild owner` are internal rebuild/review control documents, not the beginner path. Users should start from the `User / learner` rows."

This appears directly before the table header — exactly where it is needed — and the wording is unambiguous. The risk of a first-time reader following internal rebuild links without realizing their audience has been eliminated.

---

### P1-B — Blocker ledger evidence section currency

**CLOSED.**

The amended ledger's "Evidence And Gates" section now lists the current Phase H/G gate outputs explicitly: the focused 19-test run, the wording gate with `final_public_surface_gate: true`, the source-tree doctor with `status: v3_capability_branch_ready`, and the full matrix at 148 modules / 754 tests. Historical entries are labeled as pre-Phase-H/G. The section is now internally consistent and current.

---

### P1-C — Tutorial lesson coverage confirmation in wording gate

**CLOSED.**

The amended candidate states: *"The wording gate scans every lesson in `tutorials/current/`, including lessons 08–15 that teach negative routes and boundary cases."*

This is confirmed by the gate script itself: `DEFAULT_FILES` in `scripts/v3_release_wording_gate.py` (lines 201–215) explicitly lists all 15 lessons from `01_first_run.md` through `15_contact_manifold_broadphase_boundary.md`. The wording gate test (`tests/v3_release_wording_gate_test.py`, lines 309–344) explicitly asserts that lessons 09–15 appear in the scanned set and the overall gate passes. Tutorial 08 is confirmed present in `DEFAULT_FILES` even though the test does not individually assert it; the full gate run passing with `violations: []` covers this.

The note was the required addition; the underlying file coverage was already correct.

---

## New-Issue Check

No issues introduced by the amendments:

- The documentation map note does not add any prohibited wording.
- The ledger's dual-subsection "Evidence And Gates" correctly labels historical vs. current state without erasing the historical no-go.
- The candidate's gate clarity note does not assert release authorization.
- The 39-test run reported by the user (superset including `v3_public_docs_rebuild_surface_test` and `v3_rebuild_tutorial_surface_test`) is additive coverage beyond the 19-test ledger entry, consistent with Phase H/G adding more test modules. No count contradiction exists.
- All three top-level claim flags remain `false` across the candidate, the ledger, and the gate payload. The wording gate `release_authorization_note` still reads: *"Broad V3-over-V2 speed wording remains blocked because the high-performance branch did not prove that claim."*
- No V4, C ABI, embedding, DLPack, true-zero-copy, or broad speedup wording appears in any amended file.

---

## Verdict

**`accept_phase_h_g_capability_release_ready`**

All five findings (P0-A, P0-B, P1-A, P1-B, P1-C) are closed by the amendments. The dual-track blocker ledger is correct and current. The wording gate passes with no violations. The candidate correctly records that `release_authorized: false` and that the next required action is release-owner explicit authorization — not this review. This packet is ready to be forwarded to the release owner.

This verdict does not authorize public speedup wording, all-app victory, V4, embedding, C ABI, zero-copy, or any wording beyond the exact capability/quality scope described in the candidate. Authorization of those remains with the release owner.
