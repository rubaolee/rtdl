# Claude Review — Goal4833 RayJoin Debugging Method Reset

Date: 2026-06-30
Reviewer: Claude (independent external reviewer)
Under review: `history/internal_docs/call_for_review_goal4833_rayjoin_debug_method_reset_2026-06-30.md`

## Verdict

```text
verdict: approve_method_reset_and_authorize_contract_first_debugging (with required amendments)
authorized now: Goal4833-A (contract extraction, read-only of paper/author source)
gated: 4833-B..E proceed per the amendments below
not authorized: performance runs, full Section 5.7 claims, broad runs before A/B
```

The reset is clearly correct and well-reasoned. Patch-and-run against full
comparisons is uncontrolled science, and the doc's own diagnosis is exactly
right: "the same bug can appear to move between line 25 and line 90411 without
proving what changed." Moving to contract-first + minimal synthetic reproducers
is the proper method. Approve it — with amendments, because this line is allowed
to edit `src/native`, which is the project's most dangerous zone.

## What's strong (credit)

- Correct scientific ordering: paper contract → author-code contract → synthetic
  tests → public-sample regression → full stream last.
- Honest evidence hygiene: the slope-flip experiment, the unproven sort-tie
  attempt, and the halted `goal4834` run are all correctly flagged as
  **not evidence**. This is the discipline that was missing before.
- Honest data labeling: public County×Soil = real byte-equal success;
  County×Zipcode = same-source regenerated CDB, **not** exact paper input/answer.

## Required amendments

### AM1 — The synthetic contract test is the GATE that separates "general correctness fix" from "RayJoin patching"
This line allows core (`src/native`) edits "if they are generally wrong." That
boundary is exactly where the project keeps blurring into RayJoin-specific
hacks. Make the rule explicit and binding:

> A core semantics change is legitimate **only if** a minimal synthetic test
> derived from the paper/author contract shows the OLD behavior violated the
> author contract and the NEW behavior matches it. "It made RayJoin pass" is
> **not** a valid justification for a core edit.

This converts the synthetic-test method from a productivity preference into the
mechanism that prevents RayJoin-specific patching of the v2.14 core.

### AM2 — Do not grandfather the currently-in-tree unjustified changes
Two changes are already in the tree without contract-test justification:
`src/native/optix/rtdl_optix_core.cpp` (SoS `t_reported` repair) and the
`rayjoin_overlay.py` "unproven intersection sort tie attempt." Per AM1:
- **Revert the sort-tie attempt now** — it is reactive, unproven, and did not fix
  the first diff. Re-introduce only if a contract-derived synthetic test
  justifies the exact author tie-break.
- The `rtdl_optix_core.cpp` SoS change must be **re-derived and justified by a
  Goal4833-B synthetic test**, or reverted. It cannot be carried forward as
  "already done."

### AM3 — A core change requires a v2.14-WIDE regression gate, not just the public sample
Goal4833-C currently checks only that County×Soil stays byte-equal. But a change
to directed-segment point-location / SoS in the **released v2.14 core** can
silently shift the outputs of other v2.14 apps and the 10-app matrix. v2.14 is
the released line, so a point-location fix that breaks another app is a
**release regression**. Widen Goal4833-C to a **v2.14-wide regression gate**
(the full app/benchmark matrix), not just the one public sample. A core fix that
fixes RayJoin and silently changes another app is a block.

### AM4 — Add two synthetic tests
The §7 set is strong and well-targeted. Add:
- **The chain-30138 case itself** as a minimal synthetic reproducer (the equal
  scaled `xsect_y` boundary case: author expects `63 110`, streaming RTDL gave
  `106 107`). Turn the actual failing case into the regression test.
- **Rational-vs-float midpoint drift:** a test where the displayed/scaled
  coordinate is identical but the exact rational coordinate differs — this is a
  named leading hypothesis (§4.4) and needs its own controlled test.

## Answers to the nine questions

1. **Stop/reset justified?** Yes, strongly. The "bug moves between line 25 and
   90411" behavior is the textbook signature of needing minimal reproducers.
2. **Evidence summary accurate?** Yes, and honestly bounded. Caveat: the public
   sample SHA256 and author-baseline SHA are POD-path assertions I cannot verify
   from my mount — retain the raw artifacts for spot-check.
3. **No more broad runs before contract + synthetic tests?** Correct — and add
   the v2.14-wide regression requirement for any core change (AM3).
4. **Synthetic tests the right minimum?** Strong set; add the two in AM4.
5. **Missing author-code file?** The list is good. Add the author code that
   **orders/dedupes intersections along a chain** (sorting mismatch is a live
   hypothesis; likely in `output_chain.h`) and the exact **CDB coordinate
   scaling/quantization** (rational-vs-float drift hypothesis). The doc's "any
   CDB scaling / planar graph loading code" covers the latter — make it explicit.
6. **Does the direct-probe result (`face_id=11375`) shift suspicion to
   midpoint/overlay?** It is a reasonable hypothesis-narrowing, **not proof**:
   the probe used the *displayed float* coordinate, which may differ from the
   exact rational midpoint the overlay computes. Confirm via synthetic test #5
   (direct query vs overlay-midpoint at the same point). Not premature to form
   the hypothesis; premature to treat as conclusion.
7. **Keep/amend/revert the sort-tie?** **Revert** (AM2). It is unproven and
   reactive. Re-introduce only when a contract-derived synthetic test justifies
   the exact author tie-break.
8. **Does A-E prevent the inefficient pattern?** Yes — **if** AM1 (synthetic test
   as gate) and AM3 (v2.14-wide regression) are enforced. Without them, A-E could
   still degrade into patch-and-run with extra ceremony.
9. **Evidence required before another full streaming compare?** All of: 4833-A
   contract extracted; 4833-B synthetic contract tests pass; public-sample
   regression preserved; **v2.14-wide regression preserved**; and the chain-30138
   first-diff has a minimal synthetic reproducer that the core/app change
   provably fixes. Only then a full County×Zipcode stream.

## Non-authorization

Authorizes Goal4833-A (read-only contract extraction) and the contract-first
method, with the amendments. Does not authorize performance runs, full Section
5.7 claims, broad RTDL speedup claims, V3/V4 or Embree work, public
docs/tutorial/release-surface edits, RayJoin-only hidden kernels, citing old
V4/Goal4806 dirty artifacts, or carrying forward unjustified core changes.
