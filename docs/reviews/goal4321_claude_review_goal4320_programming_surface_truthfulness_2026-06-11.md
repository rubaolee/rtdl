# External Review: Goal4320 Programming Surface Truthfulness

Date: 2026-06-11
Reviewer: Claude (Sonnet 4.6), external read-only review
Verdict: `accept`

## Scope

This review covers the files listed in the Goal4320 handoff. No runtime code
was changed; the review is limited to doc truthfulness and learner clarity.

---

## Check 1: Three-surface story is present and distinct

**Result: pass**

`docs/learn/programming_surfaces.md` names all three surfaces explicitly in a
table with a "What it is not" column:

| Surface | Negative boundary stated |
| --- | --- |
| Kernel DSL | "Not a promise that every high-performance benchmark route is written as `@rt.kernel` today." |
| Primitive and prepared front doors | "Not an app-specific private engine. The primitive must remain generic." |
| Partner continuation | "Not automatic partner selection, arbitrary acceleration, or a replacement for RT traversal." |

The Practical Rule section then gives a concrete primitive-discovery code
snippet and a decision tree (new generic primitive / partner continuation /
plain Python). The Kernel DSL Boundary section adds a plain prose statement:
"It is not yet the only route to performance." The Benchmark Apps section
reinforces: "Benchmark apps are reference compositions … not evidence that
every user app should be written by copying one app-specific API."

The `README.md` front page (lines 98–102) states the same three-surface
summary inline, before referring the reader to the new page:

> RTDL currently has three public programming surfaces: `@rt.kernel` for the
> authoring shape, primitive/prepared front doors for promoted generic
> contracts, and partner continuation for explicit CuPy/Numba column work.

`tutorials/current/02_kernel_shape_and_backends.md` adds: "The kernel shape
is the mental model, not the only performance entry point."

The distinction is present, consistent across files, and phrased at learner
level.

---

## Check 2: `@rt.kernel` no longer implied as sole or guaranteed performance path

**Result: pass**

Before Goal4320, the front page contained the phrase "describe the traversal-
heavy part as an RTDL kernel" which framed `@rt.kernel` as the primary
vocabulary for the performance path. The test
`test_front_page_no_longer_claims_kernel_is_the_whole_rt_path` asserts that
phrase is absent and that the corrected language is present. Both assertions
pass against the current `README.md`.

The `@rt.kernel` code example is still shown in "What You Write" — that is
correct; it teaches the shape. But the prose immediately following it now
redirects performance-oriented readers toward the three-surface summary and
the `programming_surfaces.md` link.

Tutorial `02_kernel_shape_and_backends.md` now explicitly says "Current
benchmark-quality routes often use primitive discovery and prepared front doors
directly." That is the key corrected sentence and it is in the right place
(the tutorial most likely to create the old misimpression).

---

## Check 3: App-agnostic engine rule and primitive-first guidance preserved

**Result: pass**

The "Design In One Page" table in `README.md` is unchanged and still enforces
the two-layer rule: Python owns app logic; RTDL owns the kernel contract and
backend dispatch. The text "the native engine must stay app-agnostic" is
present.

`programming_surfaces.md` repeats the constraint in the Kernel DSL Boundary
section: "app policy stays in Python; native engine contracts stay app-
agnostic." The Practical Rule section leads with `rt.find_primitive` and
makes primitive-first the documented starting point, which preserves the
guidance that existed in `primitive_discovery_workflow.md`.

The links at the bottom of `programming_surfaces.md` point to
`primitive_discovery_workflow.md`, `prepared_execution_pattern.md`,
`partner_choice_for_custom_logic.md`, `current_claim_boundaries.md`, and
`rt_core_evidence_matrix.md`. All five targets appear in the claim-scan's
`public_files_scanned` list, confirming they exist as reachable docs.

---

## Check 4: Public-doc scan remains clean

**Result: pass**

The persisted scan artifact
(`docs/reports/goal4248_current_public_docs_claim_boundary_scan.json`)
records:

- `status: "pass"`
- `hard_blocker_count: 0`
- `hard_blockers: []`
- `public_file_count: 35`
- `finding_count: 116` (≥ 90, satisfying the test floor)
- All ten `claim_boundary` flags remain `false`:
  `release_authorized`, `public_speedup_claim_authorized`,
  `whole_app_speedup_claim_authorized`, `broad_rt_core_claim_authorized`,
  `rtdl_beats_rayjoin_claim_authorized`, `paper_reproduction_claim_authorized`,
  `true_zero_copy_claim_authorized`, `automatic_partner_selection_authorized`,
  `amd_performance_claim_authorized`, `package_install_claim_authorized`

The new file `docs/learn/programming_surfaces.md` is included in the 35-file
scan set. Its one sensitive phrase ("Not automatic partner selection") is
correctly classified as `accepted_boundary_or_negative_context` — it appears
inside a "What it is not" disavowal, not an affirmative claim.

The `goal4248_current_public_docs_claim_boundary_scan_test.py` live-scan test
(which re-runs the scanner against the current working tree) also passes per
the handoff report (5 tests in that suite, 5 pass).

---

## Check 5: Report is honest that no lowering bridge was implemented

**Result: pass**

`docs/reports/goal4320_programming_surface_truthfulness_2026-06-11.md` states
clearly in the Boundary section:

> Goal4320 does not implement a new lowering bridge from arbitrary
> `@rt.kernel` programs to every prepared high-performance route.

It further enumerates what was not done: no benchmark app moves, no runtime
behavior change, no release authorization, no new public claim surfaces. The
report's self-verdict (`accept-with-boundary`) accurately reflects that this
is a doc-only step with a forward pointer to what would be needed if the
kernel DSL itself were to become the main performance route.

The test `test_report_documents_scope_and_boundary` verifies the phrases
"does not implement a new lowering bridge" and "does not authorize" are
present. Both assertions hold.

---

## Test Coverage Assessment

`tests/goal4320_programming_surface_truthfulness_test.py` contains 5 tests:

| Test | What it guards |
| --- | --- |
| `test_canonical_programming_surface_page_names_three_surfaces` | Key phrases and negative statements present in `programming_surfaces.md` |
| `test_public_front_doors_link_to_programming_surface_boundary` | All 5 front-door files contain the `programming_surfaces.md` link |
| `test_front_page_no_longer_claims_kernel_is_the_whole_rt_path` | Old problematic phrase absent; corrected three-surface wording present |
| `test_kernel_tutorial_marks_kernel_shape_as_mental_model` | Tutorial 02 contains the corrected mental-model framing |
| `test_report_documents_scope_and_boundary` | Report includes scope and boundary language |

Coverage is proportionate to the change: every modified doc has at least one
assertion. The tests guard the specific sentences that carry the truthfulness
claim rather than testing structural properties that could pass vacuously.

Grep confirms the `programming_surfaces.md` link appears in 7 files (5 are
tested; 2 additional are the handoff doc and the Goal4320 report itself —
both appropriate).

---

## Observations

No findings that block acceptance. One minor note for the record:

- The `programming_surfaces.md` "See also" links use bare relative paths
  (e.g., `primitive_discovery_workflow.md`). These resolve correctly within
  the `docs/learn/` directory for rendered markdown but would break if the
  file were moved. This is consistent with existing link style in the
  `docs/learn/` subtree and is not a Goal4320 regression.

---

## Summary

Goal4320 makes a targeted, honest correction: it names the three current
programming surfaces explicitly at the front page, in the kernel tutorial,
and in a new dedicated reference page. It does not overstate what was done.
The claim scan stays clean. The primitive-first and app-agnostic-engine rules
are preserved. Tests are meaningful and verify the key changed sentences.

**Verdict: `accept`**
