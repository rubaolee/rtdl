# Goal 532: Claude Release Authorization Review

Date: 2026-04-18
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Tag Safety

It is safe to create and push annotated tag `v0.8.0` **after the Goal532 commit
is made**. The worktree currently has uncommitted changes (the Goal532 release
conversion edits and the three new Goal532 files). The tag must be placed on the
Goal532 release commit, not on pre-commit HEAD `37084a6`. Once the commit lands,
no further gate blocks tagging.

## Evidence Checked

### Tests: Goals 530–532 — all pass

```
Ran 10 tests in 0.001s
OK
```

All 10 subtests across `goal530`, `goal531`, and `goal532` test modules pass
against the current working tree.

### Release package integrity

- All five v0.8 release package files exist and are readable.
- `release_statement.md`: states `Status: released as \`v0.8.0\`` and
  `current released version is \`v0.8.0\``; does-not-claim table present;
  performance boundary explicitly bounded to Goal507/509/524 evidence.
- `support_matrix.md`: all six apps listed; Vulkan intentionally blocked for
  robot collision screening; Goal529 `88/88` harness result recorded.
- `audit_report.md`: verdict is `Status: **ACCEPT**`; all six audit dimensions
  (app suite, programming model, scope, docs, validation, performance, history)
  pass.
- `tag_preparation.md`: states `Tag \`v0.8.0\` is authorized for the Goal532
  release commit`; required preconditions recorded.
- `README.md` (v0_8): states `released as \`v0.8.0\`` and
  `current released version is \`v0.8.0\``.

### Stale candidate wording

No live instances of `Release-Candidate`, `release candidate / not yet tagged`,
`current released version remains \`v0.7.0\``, `not authorized for tag yet`,
or `Do not tag \`v0.8.0\` yet` remain in the public v0.8 release package or
tests. Confirmed by Goal532 test `test_v08_release_package_no_longer_claims_candidate_status`.

### Public link chain

- `README.md` (front page): links `RTDL v0.8 Release Package`,
  `RTDL v0.8 Release Statement`, `RTDL v0.8 Support Matrix`; states
  `current released version: \`v0.8.0\``.
- `docs/README.md`: v0.8 release package link appears before v0.7 link;
  states `current released version is \`v0.8.0\``.
- `docs/current_architecture.md`: links v0.8 Release Statement and Support Matrix.
  All three Goal531 public-link tests pass.

### Pre-release gate chain

- Goal528 macOS audit: `232` tests OK, `62/62` harness commands pass.
- Goal529 Linux validation: `232` tests OK, `88/88` harness commands pass;
  Embree/OptiX/Vulkan probes all pass.
- Goal530 release-candidate package: accepted by Claude, Gemini, and Codex.
- Goal531 public links: accepted by Claude, Gemini, and Codex.
- User authorization: explicit on 2026-04-18 conditional on pre-release gates
  passing (all gates passed).

### Honesty boundary

v0.8 is accurately described as an app-building release over the v0.7.0 surface.
No overclaims exist for ANN indexing, production clustering, full robotics,
N-body simulation, or general speedups. Performance claims are tied to specific
goal runs. The v0.7 DB/language/backend contract is not widened.

## Required Step Before Tagging

The worktree is not yet clean — the Goal532 release conversion and the three new
Goal532 files (`handoff` doc, `reports` doc, `goal532` test) must be committed
first. The tag goes on that Goal532 release commit.

## Verdict

**ACCEPT.** All documentation, tests, boundary claims, and public links are
coherent and clean. Creating and pushing annotated tag `v0.8.0` on the Goal532
release commit is authorized.
