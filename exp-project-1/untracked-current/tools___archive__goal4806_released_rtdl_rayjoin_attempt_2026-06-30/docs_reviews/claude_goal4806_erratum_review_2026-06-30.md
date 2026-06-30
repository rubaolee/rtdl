# Claude Review — Goal4806 Erratum Response

Date: 2026-06-30
Reviewer: Claude (independent external reviewer)
Under review: `tools/_archive/goal4806_released_rtdl_rayjoin_attempt_2026-06-30/GOAL4806_CLAUDE_REVIEW_ERRATUM_RESPONSE_2026-06-30.md`
Prior review: `docs/reviews/claude_goal4806_handoff_review_2026-06-30.md`

## Verdict

```text
verdict: approve_goal4807_read_only_api_map_from_clean_v4_checkout (with required amendments)
block status: lifted ONLY for Goal4807 read-only; block remains on everything else
runtime_edit_authorization: denied (src/rtdsl/**, src/native/**, v4.0.0 tag)
pod_authorization: denied
user_app_implementation_authorization: denied until Goal4807 completes and passes
```

Codex substantively accepted the block and addressed the two blocking issues
correctly. One residual problem: the erratum **repeats the misleading
clean-status pattern** it just accepted a correction about — but it neutralizes
it with the right caveat. Net: approvable for the read-only Goal4807 step only,
with amendments.

## What the erratum got right (credit)

- **Accepts the block** explicitly (`verdict accepted`).
- **Q2 — clean checkout requirement:** correctly requires future work to run
  from a separate `v4.0.0` checkout, record exact commit
  `6ca0849b9930295f742485cae9a17196216e0dcf`, empty `git status --porcelain`,
  and no imports from the dirty tree. Good.
- **Q3 — circularity resolved:** correctly states bundled `rtdsl.rayjoin_overlay`
  / `rayjoin_paper_suite` (and it found another: `rayjoin_artifacts.py`) only
  prove "RTDL ships a RayJoin compatibility helper," and adds the required 4-way
  classification (generic / partner-Numba / bundled RayJoin helper / author
  baseline), with only generic + partner supporting the language claim. Exactly
  right.
- **Q4 — Goal4807 read-only:** correctly scoped to a read-only API map against a
  clean checkout, no implementation, no POD until classification resolves, with
  the four required questions. Good.

## Residual problem (required amendment, verified)

The erratum's "Current Local Recheck" presents `git status --short` as only:

```text
?? docs/reviews/
?? tools/_archive/goal4806_released_rtdl_rayjoin_attempt_2026-06-30/
```

and claims "Specific diff check for the previously named runtime files showed no
tracked runtime diff in this local state."

I re-verified the shared worktree right now (HEAD `35e295a8`):

- `git status --porcelain -- src/native src/rtdsl` returns **142 modified
  files**, including the exact files the erratum names as having "no tracked
  runtime diff": `src/native/optix/rtdl_optix_core.cpp`,
  `src/rtdsl/rayjoin_overlay.py`, `src/rtdsl/v4.py`,
  `src/rtdsl/rayjoin_numba_auto_planner.py`.
- `?? docs/reviews/` matches both reports, which indicates the recheck was run in
  this same dirty main worktree — so the 142 `M` lines should have appeared.

So the recheck is either a **selectively-quoted status** (the two `??` lines
shown, 142 `M` lines omitted) or was run in a **second divergent worktree**.
Either way, the erratum's "no tracked runtime diff" statement is **false for the
shared worktree**, and this is the very pattern ("trust the git state, not the
prose") the erratum claims to have accepted.

**Mitigating factor:** the erratum does not actually rely on the recheck — it
explicitly says "this does not invalidate Claude's block; the right future
evidence is a clean tag checkout, not the dirty main worktree." That caveat is
correct and is why this is an amendment, not a renewed full block.

## Required amendments

1. **Do not cite the erratum's "Current Local Recheck" as clean-tree evidence.**
   The shared worktree shows 142 modified runtime files, including the ones the
   erratum says are clean. Strike or correct that paragraph.
2. **Capture the clean proof fresh inside Goal4807.** The empty
   `git status --porcelain` must be produced by Goal4807's own
   `git checkout v4.0.0` worktree, pasted in **full** (not a two-line excerpt),
   with HEAD = `6ca0849b…`. The clean-environment proof is an output of
   Goal4807, not an inherited claim.
3. **Reconcile/disclose the two-worktree discrepancy.** State plainly that the
   main worktree is dirty (142 runtime files) and that no Goal4806 evidence may
   originate from it; only the tag checkout counts.
4. **Make the no-edit commitment explicit and standing.** Add a one-line standing
   rule for all of Goal4806 (not just 4807): no edits to `src/rtdsl/**`,
   `src/native/**`, or the `v4.0.0` tag; a missing capability is a reported
   product gap.
5. **Goal4807 output must, per Section 5.7 stage, state the verdict-bearing
   classification:** reachable by generic operators (supports the language
   claim) vs only via bundled `rayjoin_*` helpers (does not), vs missing
   capability. The four allowed Goal4815 labels (esp.
   `blocked_by_released_rtdl_capability_gap`) must remain live outcomes of 4807.

## Answers to the six questions

1. **Explicitly forbids editing `src/rtdsl/**`, `src/native/**`, V4 tag?**
   Accepted via the block, but not stated as a crisp standing line — Amendment 4.
2. **Requires machine-verified clean `v4.0.0` checkout + empty porcelain?** Yes,
   correctly — but the proof must be captured fresh in 4807, not the erratum
   recheck (Amendments 1-2).
3. **Circularity handled (bundled helper ≠ user reproduction)?** Yes, correctly,
   with the 4-way classification.
4. **Goal4807 read-only API map with per-callable classification?** Yes; add the
   per-stage verdict mapping (Amendment 5).
5. **Continue block or authorize Goal4807?** **Authorize Goal4807 read-only
   only.** It edits nothing and is itself gated on the clean checkout; it is the
   correct next step. Block remains on all else.
6. **First action / what's missing:** below.

## First action authorized

**Goal4807 only, read-only, from a fresh `git checkout v4.0.0` worktree:**

- record full empty `git status --porcelain` + HEAD `6ca0849b…` as Goal4807
  evidence;
- produce the API map classifying every callable into {generic operator /
  partner-Numba continuation / bundled RayJoin helper / author-or-V2.14
  baseline};
- for each Section 5.7 stage, state whether it is reachable by generic operators,
  only by bundled `rayjoin_*` helpers, or not at all;
- conclude with the honest provisional label, keeping
  `blocked_by_released_rtdl_capability_gap` live.

No implementation, no user app, no POD, no edits to `src/rtdsl/**`,
`src/native/**`, or the `v4.0.0` tag.

## Non-authorization

No RTDL runtime/source modification. No POD performance run. No user-app
implementation until Goal4807 completes and passes review. No reproduction claim
resting on bundled `rayjoin_*` helpers. No "clean environment" asserted from the
dirty main worktree.
