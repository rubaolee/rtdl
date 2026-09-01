# Hostile self-review of the Goal5835/Goal5836 strict audit

Date: 2026-09-01
Reviewer: Codex internal self-review only
Independent external reviewers: none
Consensus: not claimed

## 1. Review question

Does the new audit honestly distinguish executed evidence from semantic
projection, preserve frozen custody, reproduce its findings deterministically,
and avoid reopening the completed Goal5836 transaction?

## 2. Verdict

```text
PASS_WITH_CURRENT_CLAIM_NARROWING
P0 = 0
P1 = 0 after current-status remediation
P2 = 2 residual audit limitations
P3 = 1
```

The underlying audited product still has the `P1=1/P2=6/P3=1` finding
denominator recorded in the authority. This self-review scores the audit
artifact itself after its current-status remediation; it does not erase or
downgrade those product findings.

## 3. Hostile checks

| Attack | Result |
|---|---|
| Hide the Goal5835 P1 and recompute the seal | Rejected by exact finding-set policy |
| Relabel Goal5835 as executed Paper App | Rejected by counterevidence policy |
| Reopen Goal5836 or claim promotion | Rejected by terminal-verdict policy |
| Claim an external review occurred | Rejected by exact review-state policy |
| Drift any frozen Goal5834/5835/5836 input | Rejected by exact SHA or predecessor verifier |
| Replace result with recount | They are already byte-identical; no discrepancy hidden |
| Regenerate Goal5835 on Mac | Equal after removing only known absolute-path fields |
| Ignore direction because edge IDs are canonical | Duplicate-ID probe proves coordinates still reverse |
| Trust generic output shape blindly | Malformed-output probe demonstrates current acceptance |
| Infer positive mesh coverage from the app name | Coverage derivation reports zero positive complete-mesh rows |

The receipt's fixture loader does invoke triangle-edge deduplication for the
single complete-triangle miss row. The audit distinguishes that indirect
negative-boundary check from direct receipt use and from positive mesh
construction; it does not claim that the function is absent from the entire
call graph.

The 20 hostile tests include coordinated re-sealing, not just stale-seal
attacks. A freshly generated authority also round-trips exactly.

## 4. Residual limitations

### P2-1: The authority seal is not external authenticity

The builder and tests live in the same repository. The internal seal prevents
accidental drift and blocks the encoded hostile mutations, but a coordinated
malicious rewrite of builder, tests, authority, and Git history is outside this
model. Git remote identity, capsule verification, and later external review are
separate controls. The report states this explicitly.

### P2-2: Goal5836 semantics remain review-dependent

The audit rechecks exact evidence bytes and the complete author-direction call
chain. It also visually rechecked the exact paper pages. It does not derive the
semantic result through a formal graph proof or mechanically interpret the
PDF. Independent external semantic review remains useful and is deferred, not
silently treated as complete.

### P3-1: Current-status remediation is append-only

The hash-bound Goal5835 README still ends with a now-historical statement that
Goal5836 is required. Editing it would invalidate predecessor custody. The new
`CURRENT_STATUS_AFTER_GOAL5836.md`, `START_HERE.md`, and `AGENTS.md` overrides
must therefore remain visible to current readers. A future documentation
reorganization should clearly distinguish frozen historical documents from
current operational documentation.

## 5. Scope checks

- No Claude, Gemini, subagent, or external service was used for this review.
- No external consensus is claimed.
- No pod, GPU, author build, RTDL execution, or timing was needed.
- No Goal5835/Goal5836 historical result, report, authority, or hash-bound app
  source was changed.
- No CGO experiment or performance statement was added.

## 6. Final response

Accept the audit as the controlling internal correction of current claim
scope. Keep external review as explicit debt until the owner returns. Treat any
implementation repair as a new goal with prospective evidence rather than a
continuation of Goal5836.
