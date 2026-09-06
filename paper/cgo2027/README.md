# CGO 2027 anonymous manuscript workspace

`main.tex` is the current anonymous working manuscript, but it predates the
post-Goal5851 scope adjudication and is **not submission-ready**. R4 must rewrite
the complete paper around bounded whole-protocol compilation: shared
schema/identity/lifecycle checks plus topology-specific trusted lowering. It
must not claim arbitrary Callback IR, topology-generic lowering, intrinsic
language speedup, broad usability, or a representative unseen-application
study.

## Current evidence branch

- Measured implementation M:
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`.
- Predecessor E:
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`.
- Two exact tasks passed the machine numerical contract independently on RTX
  4090 Ada and RTX 3090 Ampere. The main performance observation is prepared
  public RTDL/Direct; no A/D worst-block gate exists.
- The original written per-execution detailed-receipt requirement was not
  fulfilled. No wrong output was observed in the retained final GPU samples;
  native/compact status and explicit output-oracle checks remained synchronous.
- Implementation-entry is not an authorized positive performance claim.
  Post-import is adverse on all four rows and reaches `2.377129x`. Relative to
  E, first-result medians regress about 8%--22% at entry and 16%--31%
  post-import; those rows are post hoc and non-gating. Both first-result
  endpoints are lifecycle/import-confounded.
- The separate paired ON/OFF instrumentation study measured Arm A only.

The sentence-level ledger and raw-to-table reconstruction are in:

```text
history/internal_docs/post_goal5851_submission_remediation_20260906/CLAIM_LEDGER.json
history/internal_docs/post_goal5851_submission_remediation_20260906/R2_SUBMISSION_EVIDENCE_REPORT.md
history/internal_docs/post_goal5851_submission_remediation_20260906/R3_CONTROL_AND_CUSTODY_CORRECTION_LEDGER.md
```

## Artifact state

`artifact_post_goal5851/` is a committed template and verifier-source root; it
is never a generated output root. R2 successfully built two byte-identical
packages in new repository-external directories and replayed an extracted copy
under a foreign path in normal and optimized Python without project imports.
That is a pre-F rehearsal only. The successful chain must be repeated from a
clean checkout of committed final tooling snapshot F before it can support the
submission artifact.

## Remaining gates

1. Commit candidate F and complete the clean-checkout export, deterministic
   twin build, foreign-path offline replay, identity scan, and hash binding.
2. Rewrite and render the full manuscript from the R2 projection and R3
   correction ledger.
3. Build the corresponding final anonymous package and replay the exact final
   bytes.
4. Obtain review of the actual final PDF and package. Earlier reviews are
   pre-final input, not final-byte authorization; external human authoring
   evidence remains zero.
5. Complete page-limit, formatting, bibliography, anonymity, link, and upload
   checks. Record submission only after an authorized upload actually occurs.

The hard executable-code freeze is 2026-09-08 00:00 America/New_York. After
that point, only frozen-tool execution, manuscript/bibliography edits, claim
narrowing, evidence preservation, packaging/replay, review, and submission
checks are permitted.
