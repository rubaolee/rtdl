I have now read all required context. Formulating the review.

---

# Claude External Review: Phoenix V3 Phase H/G Capability Completion Candidate

**Date:** 2026-06-24
**Reviewer:** Claude (claude-sonnet-4-6)
**Packet:** `docs/rebuild/v3/phoenix_v3_phase_h_g_capability_completion_candidate_2026-06-24.md`

---

## Verdict

**`accept_with_required_amendments`**

The structural logic is sound. The Phase A→H fork is correctly recorded and respected. No high-performance path is reopened. The claim-boundary apparatus is substantive and machine-checked. The dual-track blocker ledger is correctly structured. The user-facing front doors are honest. Two required amendments and three recommended amendments must be resolved before the packet is forwarded to release-owner authorization.

---

## Question-by-Question Findings

### Q1 — Does the packet correctly follow the Phase A No-Go fork into Phase H?

**Yes.**

The candidate opens with an exact quotation of the Phase A exit gate:

```text
phase_a_exit_gate_met: false
phase_a_complete: true
next_phase: H capability/quality release planning
continue_phase_a_candidate_search: false
continue_to_phase_b_high_performance_path: false
```

This is sourced from the three-way consensus document, cross-verified independently by Claude and Antigravity. The Phase H status file and the blocker ledger both back-reference the same consensus artifact. The chain of custody is clean: Phase A closed → consensus recorded → Phase H opened → capability scope defined.

---

### Q2 — Does it avoid reopening Phase B/C/D high-performance work after A failed?

**Yes, with one observation.**

The packet does not reopen the high-performance path. The RTNN Phase A result (`1.03622547722238x` against a `>=1.20x` bar) is correctly characterized as "trunk-proof/control with no further tuning." The Barnes-Hut result is correctly closed as parity. The blocker ledger records `high_performance_release_status: redo_required`, preserving the historical failure record rather than erasing it.

**Observation (non-blocking):** The blocker ledger's narrative description "V3 major release requires broad V2.x performance superiority" is labelled "Historical high-performance branch rule, preserved so scanners and reviewers do not forget the failed claim boundary." This phrasing is correct but someone reading quickly might misread it as a current requirement blocking the capability branch. The next sentence clarifying the dual-track split is adequate but dense. No amendment required; flagged for awareness.

---

### Q3 — Are all broad performance, release, V4, embedding, C ABI, and zero-copy claims blocked?

**Yes, and the machine enforcement is unusually thorough.**

The wording gate (`scripts/v3_release_wording_gate.py`) enforces:

- **10 positive-overclaim regex patterns** catching: "v3 is released," "v3 is complete," "v3 broadly beats v2," "RTDL accelerates every benchmark app," "release-ready," "selecting OptiX automatically means," "v4.0.0 is the current," "v3.0.2 is the current," "release-candidate"
- **6 post-M150 leak patterns** catching: C ABI, embedding, external runtime, DLPack, true-zero-copy, non-OptiX SDK
- **6 unauthorized true-flag patterns** catching any document-level assignment of `release_authorized: true`, `public_speedup_claim_authorized: true`, `broad_v3_faster_than_v2_claim_authorized: true`, and three others
- **~200 required strings** spanning every evidence packet, boundary lesson, and forbidden expansion
- **13 expected M7 row IDs**, each exact

The gate payload hardcodes all three top-level claim flags to `false` regardless of input. The `release_authorization_note` field explicitly states: "Broad V3-over-V2 speed wording remains blocked because the high-performance branch did not prove that claim."

The candidate's version block confirms:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

These flags are consistent across the candidate, the status file, the blocker ledger, and the claim boundaries page.

---

### Q4 — Are the user-facing doors clean enough for a capability/quality V3 learner path?

**Yes, with one recommended amendment.**

**README.md:** Opens with "Status: Phoenix V3 capability/quality branch, not released." The first content paragraph correctly explains that Phase A failed. Old V3/V4 material is explicitly quarantined. The "What Is Available Now" table distinguishes source tree, examples, tutorials, rebuild docs, and history quarantine. The "Read Next" section chains to current authoritative docs only.

**tutorials/current/README.md:** Opens with "Status: capability-branch learner path, not a release tutorial set." The "Shortest Safe Path" of five lessons (01 first run → 02 hello world → 03 backend choice → 07 grouped sum → 06 claim boundaries) keeps a new user away from the evidence archive. The remaining 10 lessons explicitly teach route splits and boundary cases.

**docs/learn/current_claim_boundaries.md:** Per-row boundary language is precise and complete. The "Blocked Claims Now" section is comprehensive. The per-row caveats (e.g., "Three exact `aabb_candidate_stream` rows are M7-qualified; that does not make full spatial-index acceleration...") directly address the most common failure mode of over-generalizing a scoped row.

**docs/public_documentation_map.md:** The map correctly segregates "User / learner" from "V3 rebuild owner" audience.

**Recommended amendment (P1):** The documentation map presents both audiences in a single unlabeled table. A first-time reader scanning the map rows for "V3 Benchmark Evidence" or "Phoenix V3 Performance Dossier" might follow those links without noticing they are labelled "V3 rebuild owner." A one-sentence introductory note — "Documents in the 'V3 rebuild owner' rows are internal rebuild control documents; users should begin from the 'User / learner' rows only" — would eliminate this ambiguity before publication.

---

### Q5 — Is the dual-track blocker ledger correct?

**Yes.**

The blocker ledger (`v3_release_authorization_blockers_2026-06-20.md`) is correctly dual-track:

| Track | Status |
|---|---|
| Capability/quality branch | `pending_external_review` |
| High-performance branch | `redo_required` |

The three current open P0 blockers are correctly enumerated:

1. Capability/quality external review not obtained — addressed by this review packet.
2. Release-owner authorization not obtained — correctly preserved as a separate gate.
3. Broad V2.x performance not proven — correctly noted as "not a blocker for the capability/quality branch" but permanently blocking broad speedup wording.

The "Closed, Scoped, Or Non-Claim Items" table is comprehensive and internally consistent: the 13-row surface is correctly described as `source_tree_pod_gated_thirteen_row` scope, the installer scope waiver is correctly bounded, and the secondary RT hardware waiver is correctly limited to `single_rtx_4000_ada_driver_550_127_05_pod`.

---

### Q6 — Are the listed local gates adequate for external release-readiness review?

**Adequate in substance, but one numeric discrepancy requires explanation.**

The gate suite is:

| Gate | Reported Result |
|---|---|
| 19-test focused suite | OK |
| `v3_release_wording_gate.py --pretty` | `status: pass`, `violations: []` |
| `rtdl_source_tree_doctor.py --json --run-smoke` | `ok: true`, `v3_capability_branch_ready` |
| Full `v3_rebuild` matrix | `module_count: 148`, `tests: 754`, `status: OK` |

The wording gate is the most substantively important gate and it is exceptionally thorough (see Q3).

**Required amendment (P0-A):** The blocker ledger's "Evidence And Gates" section records `full v3_rebuild matrix: 106 modules / 509 tests OK`, but the candidate reports `module_count: 148, tests: 754`. This is a difference of 42 modules and 245 tests. If Phase H/G added these (which is consistent with H/G extending the test suite), that is material new coverage and the ledger must be updated to reflect the current matrix count. If the numbers mean different things (e.g., module vs file counting changed), that must be explained. Either way the discrepancy should not be left unresolved in the ledger used as the authoritative source of current gate state.

**Required amendment (P0-B):** The candidate reports "19 tests OK" across five test groups, one of which is `v3_phoenix_release_readiness_gate_test`. However, the same candidate section reports `readiness gate: redo_required`. A reader unfamiliar with the test suite structure will reasonably ask: how can the readiness gate test pass if the gate itself reports redo_required? A one-sentence clarification is required: the test verifies that the gate correctly identifies and reports the redo-required state — i.e., the test is checking gate logic, not asserting release readiness. Without this note, the "19 tests OK" line alongside "readiness gate: redo_required" creates a contradiction in the packet's own evidence section.

---

### Q7 — What exact amendments are required before release-owner authorization?

#### Required Amendments (P0) — Must be resolved before forwarding to release-owner

**P0-A: Test matrix count discrepancy in blocker ledger.**

- **Where:** `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`, "Evidence And Gates" section.
- **Current state:** Lists `full v3_rebuild matrix: 106 modules / 509 tests OK`.
- **Candidate state:** Reports `module_count: 148, tests: 754, status: OK`.
- **Required action:** Update the ledger's evidence section to reflect the current matrix count, with a brief note on why the count changed (Phase H/G additions). If the counts refer to different measurement methods, document the distinction.

**P0-B: Gate clarity — release readiness test vs. readiness gate status.**

- **Where:** `docs/rebuild/v3/phoenix_v3_phase_h_g_capability_completion_candidate_2026-06-24.md`, "Current Local Gates" section.
- **Current state:** "19 tests OK" followed by `readiness gate: redo_required` with no explanation of the apparent contradiction.
- **Required action:** Add a parenthetical: "(The `v3_phoenix_release_readiness_gate_test` verifies that the gate correctly reports `redo_required` for the high-performance mandate; this is expected behavior, not a test failure.)"

#### Recommended Amendments (P1) — Must be resolved before publication

**P1-A: Documentation map audience segregation.**

- Add a one-sentence note above the "Current Doors" table in `docs/public_documentation_map.md` clarifying that "V3 rebuild owner" rows are internal rebuild control documents, not user documentation.

**P1-B: Blocker ledger evidence section currency.**

- The "Evidence And Gates" section of the blocker ledger still references gate artifacts from 2026-06-21 (readiness gate, aggregate readiness gate, breadth gate). Phase H/G added the source tree doctor capability check and the new wording gate run with `final_public_surface_gate: true`. The ledger should reference the current gate artifacts alongside the historical ones.

**P1-C: Tutorial lesson content verification.**

- The packet reports the wording gate passes across all scanned files, which covers `tutorials/current/README.md` but does not individually verify the internal content of each lesson file against the claim boundaries. Before release-owner authorization, each lesson in `tutorials/current/` (particularly lessons 08–15, which cover negative routes and boundary cases) should have their boundary wording spot-checked or confirmed covered by the wording gate scan. If the gate already covers these files, a note confirming they are in `DEFAULT_FILES` should be added to the candidate.

---

## Non-Findings

The following are explicitly confirmed clean and are not open items:

- No V4 material in the user path. Old V3.0.2 and V4 front doors are quarantined under `docs/history/quarantine_v3_v4_reset_2026-06-20/`.
- No C ABI, embedding, DLPack, or true-zero-copy wording in the current surface.
- No broad V3-over-V2 speedup claim. The `1.012x` same-row geomean is correctly characterized as "near parity," not a performance source.
- No third Phase A candidate search. The anti-avoidance lock is correctly honored.
- The 13 M7 row IDs are exact and consistent across the candidate, the blocker ledger, the claim boundaries page, the README, and the wording gate's `EXPECTED_ROW_SCOPED_M7_IDS` tuple.
- The `VERSION` and `pyproject.toml` are correctly set as branch markers (`v3-capability-branch-2026-06-24` / `3.0.0.dev20260624`), not release markers.

---

## Summary

Two required amendments (P0-A: ledger matrix count, P0-B: gate clarity note) and three recommended amendments (P1-A: documentation map note, P1-B: ledger evidence currency, P1-C: tutorial lesson coverage confirmation) must be applied. After those amendments are recorded and the local gates rerun to confirm no regressions, this packet is structurally ready to be forwarded to the release owner for explicit authorization of the capability/quality V3 branch. This review does not itself authorize the release.
