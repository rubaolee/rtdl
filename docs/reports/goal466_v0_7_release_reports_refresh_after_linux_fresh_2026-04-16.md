# Goal 466: v0.7 Release Reports Refresh After Linux Fresh Validation

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The v0.7 release-facing branch reports have been refreshed to include Goal 464
Linux fresh-checkout validation while preserving the no-tag and no-release
boundary. The refresh is accepted with 2-AI consensus.

## Files Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`

## Changes Made

Release statement:

- adds Goal 464 Linux fresh-checkout validation to the v0.7 evidence base
- records that fresh synced checkout import, OptiX/Vulkan backend builds,
  backend probes, PostgreSQL availability, focused tests, and app demos passed
- preserves Goal 452 as canonical performance wording
- adds Goal 464 as canonical fresh-checkout validation
- states the GTX 1070 no-RT-core caveat

Support matrix:

- adds a Linux fresh-checkout validation section
- links to the Goal 464 report
- states the backend bring-up, PostgreSQL, demo, and hash-match facts
- states the GTX 1070 no-RT-core caveat

Audit report:

- updates audit scope through Goal 466
- adds the fourth branch pass for app-facing demos and fresh-checkout
  validation evidence
- keeps the bounded/non-DBMS boundary
- states that Goal 464 is not RT-core hardware-speedup evidence

Tag preparation:

- updates release-gated state through Goal 464
- keeps `Do not tag v0.7 yet`
- adds app-level and kernel-form demo readiness
- adds fresh Linux checkout validation readiness
- states the GTX 1070 no-RT-core caveat

## Verification

Manual checks:

- read edited sections back with `sed`
- checked release-facing references with `rg`
- verified git index staged path count remains `0`

## Boundary

- staging performed: `false`
- release authorization: `false`
- no tag is authorized
- no merge to main is authorized

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal466_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal466-v0_7-release-reports-refresh-after-linux-fresh.md`
