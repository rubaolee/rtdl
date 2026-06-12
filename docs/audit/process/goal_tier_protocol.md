# Goal Tier Protocol

Status: current internal process rule for reducing ceremony while preserving
claim discipline.

This protocol responds to the project-health risk that every small change was
starting to require a full registry, report, test, and multi-AI consensus
packet. The fix is not to weaken release discipline. The fix is to classify
goals by risk.

## Tier A: Light Goals

Use Tier A for work that cannot create a public performance, release, roadmap,
or architecture-boundary claim.

Examples:

- typo fixes,
- link fixes,
- current-doc curation,
- secret redaction,
- low-risk report cleanup,
- local ignore-rule hardening,
- small test-name or path repairs,
- compatibility re-exports with no behavior change.

Minimum closure:

- exact changed files are reviewed by the implementer,
- focused tests or link/scan checks run when applicable,
- final summary names any remaining risk.

No dedicated report, registry dataclass, or external-AI review is required by
default. Add them only when the change touches public wording or could alter
evidence interpretation.

## Tier B: Runtime Or Contract Goals

Use Tier B for behavior or contract work that changes how RTDL executes,
validates, dispatches, or exposes a primitive/partner path, but does not by
itself authorize a release or public claim.

Examples:

- new generic primitive implementation,
- partner continuation kernel,
- prepared-session behavior,
- benchmark runner behavior,
- app front-door behavior,
- source-tree doctor behavior,
- refactor of a shared runtime module.

Minimum closure:

- focused executable tests,
- report or design note if the behavior is nontrivial,
- artifact when hardware behavior matters,
- 2-AI consensus for important contract changes when an external reviewer is
  available; otherwise write the review handoff and record the missing review.

## Tier C: Claim, Roadmap, Release, Or Major Evidence Goals

Use Tier C for anything that can change how users, reviewers, or release notes
understand RTDL.

Examples:

- release authorization,
- public speedup wording,
- RT-core evidence interpretation,
- partner recommendation policy,
- roadmap version changes,
- architecture boundary changes,
- zero-copy/device-residency wording,
- broad benchmark adequacy claims.

Minimum closure:

- written report,
- focused tests or evidence artifacts,
- explicit claim-boundary section,
- 3-AI consensus when the project rules require it,
- no release/tag/publish action until the user explicitly authorizes it.

## Default Rule

If a goal is ambiguous, treat it as Tier B. If it touches public claims,
release status, roadmap, architecture boundaries, or promoted performance
evidence, escalate it to Tier C.

## Non-Negotiable Boundaries

The tier protocol does not relax these rules:

- Native engine remains app-agnostic.
- Package-install wording remains blocked unless packaging is validated.
- Broad speedup and whole-app acceleration wording remain blocked without
  reviewed same-contract evidence.
- True zero-copy wording remains blocked without measured device-residency
  evidence.
- Automatic partner selection remains blocked unless separately designed,
  measured, reviewed, and authorized.

## Current Examples

| Goal | Tier | Reason |
| --- | --- | --- |
| Goal4303 current secret redaction guard | A | Security hygiene with focused scan tests; no public performance or release claim. |
| Goal4301 Numba grouped top-k device rank | B | New generic partner continuation contract; executable tests and report required. |
| Future timing-floor ten-app packet | C | Changes promoted benchmark evidence interpretation and needs pod evidence plus external review. |
| Future kernel-DSL bridge pilot | C | Decides the language identity and public programming model. |
