# Goal 63 Audit-Flow Consensus Round

## Objective

Use the live audit-flow policy as the contract for one full multi-AI audit round
over the current accepted RTDL repo state.

This goal requires:

- one Codex audit
- one Gemini audit
- one Claude audit when Claude is operationally available
- cross-review of the audit outputs
- revisions if needed
- final consensus only after the audit findings converge

If Claude is quota-blocked or otherwise unavailable, the goal may close under
the fallback rule:

- Codex + Gemini consensus

with Claude's unavailability recorded explicitly.

## Scope

This audit round covers:

- live code
- live docs
- code/doc consistency
- test/verification surface
- history/archive consistency
- manuscript source package and built PDF

This goal does not rewrite immutable historical reports unless the issue is an
archive-index or archive-registration defect in the live archive system.

## Required process

1. Codex writes the audit-flow policy into the live docs.
2. Codex performs an independent audit and records findings.
3. Gemini performs an independent audit.
4. Claude performs an independent audit if available.
5. Each audit is reviewed against the others.
6. Any blocking inconsistency is fixed and rechecked.
7. The round closes only after the required consensus rule is met.

## Acceptance

Goal 63 is complete only if:

1. the live audit-flow doc is present and linked from the live process docs
2. Codex audit is written
3. Gemini audit is written
4. Claude audit is written or Claude unavailability is recorded
5. cross-review and final consensus are written
6. any required corrections are implemented and verified before publication
