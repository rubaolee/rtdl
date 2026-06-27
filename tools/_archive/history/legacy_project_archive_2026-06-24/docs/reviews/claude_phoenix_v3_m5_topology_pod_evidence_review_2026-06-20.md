I'll proceed directly with the review using the detailed evidence already provided in your request, since the question tool isn't returning a response either.

---

## Review: Phoenix V3 M5 Topology Pod Evidence (2026-06-20)

### 1. Verdict: **Approve with amendments**

The evidence is honest about its own limits — `release_authorized: false`, `public_speedup_claim_authorized: false`, `rt_core_speedup_claim_authorized: false`, and `0` M7-qualified release rows are all stated plainly, not buried in a footnote. The matrix passes (17 modules/59 tests) and the wording gate passes with no violations. That's a legitimate "partial internal" result. But two things keep it from a clean approve.

### 2. P0/P1 issues

**P0 — none that block keeping this internal.** Nothing here is being smuggled into release/public claims; the gates that would catch that (`v3_release_wording_gate.py`) pass.

**P1 — the PIP "safe100k" directory name is stale and misleading.** The methodology is now `backend_parity_filtered_random_bbox` with a tie-rejection filter (`rejected_count: 1`), which is the right fix — but the evidence directory is still literally named `m5_pip_point_location_safe100k`, which is the exact label Codex itself identified as foolish/premature ("random bbox stream labelled 'safe' ... nearly converted a tie-sensitive result into false evidence"). Shipping the corrected methodology under the unretired old name is the kind of naming drift that causes exactly this class of mistake later when someone greps for "safe100k" and assumes the old (unfiltered) semantics. **Amendment requested:** rename the directory/file to reflect the parity-filtered methodology (or at minimum add an explicit deprecation note inside `summary.json` pointing future readers at the filter logic), before this is treated as closed.

**P1 — `query_exec` blocker has no remediation ETA or owner.** "Blocked" is honestly stated, but the evidence packet doesn't commit to next steps beyond "Codex should locate or rebuild it." For a recurring M5 cycle, an open-ended block with no tracking issue/date risks silently calcifying into permanent partial status.

### 3. Filtered-safe PIP stream repair — acceptable?

Yes, methodologically. Rejecting the one exact-tie candidate (`rejected_count: 1` out of 100,000) before timing is the correct way to avoid a near-tie row flipping the OptiX/Embree comparison due to scheduling noise rather than real algorithmic difference. The reported `1.870x` internal speedup and `2.764x` native traversal ratio are now measuring real separation, not an artifact of a coincidental tie. This is a sound fix — but see the P1 above: fixing the *method* without renaming the *artifact* is half a repair.

### 4. Are the failed attempts documented honestly?

Yes. Three failed-attempt directories are preserved on the pod with descriptive names that label their own failure mode (`failed_markdown_none`, `stopped_unbounded_query_exec_find`, `failed_pip_tie_mismatch`) rather than being deleted or silently overwritten. That's the right behavior — it leaves a trail showing the unbounded `find` was stopped (not "succeeded slowly") and that the original PIP stream had a real tie mismatch (not just "needed cleanup"). Preserving failure evidence alongside the corrected run is what makes the audit trail credible.

### 5. Should M5 status be `partial-plus internal` or stricter?

**Stricter: `partial-internal-blocked` or equivalent**, not `partial-plus`. "Partial-plus" implies the partial result is enhanced/exceeds baseline expectations. What's actually true is: internal topology evidence passed, but the author-code comparison arm — the comparison that would let this evidence mean anything against the baseline — is entirely blocked on a missing binary (`query_exec`). That's a hard blocker on the comparison axis, not a bonus on the internal axis. A status label should make a release-gate reader instantly understand "this cannot inform any release/author-parity decision yet," which `partial-internal-blocked` (or `internal-only / author-comparison-blocked`) does more precisely than `partial-plus`.

---

**Net:** the underlying engineering response to the two earlier foolish actions (unbounded find, naive "safe" label) was correct and is well-evidenced. Approve the internal evidence as-is for engineering purposes, with two amendments before calling this cycle closed: (1) rename/annotate the `safe100k` artifact to match its actual (now-correct) filtered methodology, and (2) tighten the status label away from `partial-plus` toward something that flags the author-code block as a hard gate, not a footnote.
