# Goal 333: v0.5 Public Docs Total Review Project

Date: 2026-04-13
Status: planned

## Why this goal exists

The `v0.5` preview line now has enough runtime, backend, audit, and release
material that public-document correctness is a real release risk by itself.

The repo already contains:

- front-door docs
- preview-package docs
- support and readiness docs
- external-review packet docs
- multiple imported audits

That means the next documentation task is not "write more docs". It is a
strict review project:

- is each public-facing file correct?
- is each file in the right status?
- is each file consistent with the others?
- is each important claim backed by tests or saved evidence?
- are links, paths, platform claims, and backend descriptions connected
  correctly?
- are there stale, duplicate, or misleading public docs that should not remain
  front-facing?

## Scope

This project covers the public-facing and reviewer-facing `v0.5` documentation
surface, especially:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/call_for_test.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/pre_release_plan.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/code_test_plan.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/audit_and_external_review_packet.md`

This project also permits checking linked supporting audit docs when needed to
verify status or claim integrity.

## Required audit questions

The reviewers should answer, file by file:

1. Is this file still correct?
2. Is the file in the right public/reviewer/internal status?
3. Are the version and release-state labels correct?
4. Are the backend and platform claims honest?
5. Are linked files, paths, and related packets connected correctly?
6. Does the file describe what is actually tested?
7. If it refers to evidence, is that evidence really present in the repo?
8. Is the file complete enough for its intended audience?
9. Is the file stale, duplicated, misleading, or in the wrong place?
10. Should the file stay public-facing, reviewer-facing, or internal-only?

## Required output shape

The review should be table-driven and strict.

At minimum, the review must contain:

1. A file-by-file table:
   - path
   - audience
   - status correct?
   - technically correct?
   - test/evidence connected?
   - problems
   - recommended action

2. A cross-document consistency table:
   - topic
   - files compared
   - consistent?
   - mismatch
   - recommended fix

3. A public-surface risk table:
   - risk
   - severity
   - why it matters
   - recommended fix

4. A final verdict:
   - ready as-is
   - needs bounded doc fixes
   - not ready for broader review

## Closure standard

This goal is only closed when:

- at least one external-style AI review is saved in the repo
- Codex consensus is saved
- any findings are either:
  - fixed in a bounded follow-up
  - or explicitly accepted with honest wording

Current intended bounded fixes in this slice:

- remove stale public-facing wording about `main`
- tighten preview-package and packet phase wording
- make the saved test plan more copy-paste-safe
- move internal audits and goal tracking behind explicit history paths while
  preserving link-stability stubs

## Expected next step

Launch Gemini on a strict collaborator-grade public-doc audit using this
project scope, then use a second AI consensus pass before closure.
