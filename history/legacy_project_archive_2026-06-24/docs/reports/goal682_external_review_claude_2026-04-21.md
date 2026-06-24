# Goal682 External Review — Claude

Date: 2026-04-21

Verdict: **ACCEPT**

## Scope

This review covers the v0.9.6 release-candidate package assembled in Goal682,
including the five RC files, the three public docs touched, and the boundary
constraints stated in the review request.

## Boundary Checks

**Current released version remains v0.9.5.**
Every file reviewed — README.md, docs/README.md, docs/current_main_support_matrix.md,
and all five RC files — consistently states "The current public release remains
v0.9.5." No file claims v0.9.6 is released. PASS.

**v0.9.6 is a release candidate only and is not tagged.**
All RC files carry "Status: release candidate / hold. Not tagged." The
tag_preparation.md header reads "Not tagged; do not tag yet." PASS.

**Tag/push commands present only as held commands, not to be run without
explicit maintainer authorization.**
tag_preparation.md contains the three git commands under a "Tag Commands"
section that begins with "Do not run these until the maintainer explicitly
authorizes release." The same hold requirement appears in the RC README,
release_statement, and audit_report. PASS.

**No broad DB, graph, full-row, one-shot, GTX 1070 RT-core, AMD GPU, or Apple
RT full-row speedup claim.**
Every document carries an explicit "must not claim" or "non-claims" section
covering all of these. The support matrix performance snapshot includes the
inline disclaimer: "Not allowed: broad speedup claims for DB, graph, one-shot
calls, or full emitted-row outputs." The current_main_support_matrix.md
non-claims section is equally explicit. No disallowed claim was found in any
reviewed file. PASS.

## Package Consistency

The five RC files (README, release_statement, support_matrix, audit_report,
tag_preparation) are internally consistent: the same allowed conclusion
wording, the same disallowed claim list, and the same performance numbers
appear across all of them. The performance snapshot in the RC support_matrix
exactly matches the snapshot in current_main_support_matrix.md.

The public README.md v0.9.6 entry is scoped correctly — "current release
candidate, not tagged" — and the description is bounded to the validated
prepared/prepacked 2D visibility/count work. The docs/README.md correctly
indexes all five RC files and does not promote them above release boundary.

## Gate Evidence

The review request records:
- 17 focused tests OK
- public command truth audit valid (250 commands / 14 docs)
- public entry smoke valid
- git diff --check clean

The RC audit_report additionally records:
- 1268 full local discovery tests OK, 187 skips
- Linux fresh backend gate passed (OptiX, Vulkan, HIPRT on GTX 1070)
- Codex, Claude, and Gemini Flash accepted Goal681

No test failures or audit violations were reported.

## Findings

No blocker was found. The package:
- correctly holds the tag pending maintainer authorization;
- makes no disallowed speedup claims;
- is internally consistent across all RC files and public docs;
- has complete gate evidence through Goal681;
- cleanly distinguishes the released v0.9.5 tag boundary from the
  current-main candidate surface.

The v0.9.6 release-candidate package is ready for maintainer review and
release authorization when the maintainer chooses to proceed.
