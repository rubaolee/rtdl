# V4.0 Current Status And Next Steps

Date: 2026-06-25

Status: `v4_0_0_published_goal4633_4646_wording_gate_complete`

## Current State

RTDL V4.0.0 has been published in the source tree as a bounded generic RT-core
operator release: eight documented operators beat stated brute-force
partner/CPU baselines on the frozen Goal4639 scorecard.

Goal4646 completed the tag-blocking wording fixes required by Claude's
V4.0.0 release review. The public tag is unblocked by wording review.

Pre-Goal4646 release-chain commit:

`b8528c67d V4 Goal4644 post-release guardrails`

Publication commit:

`c58642326 Publish V4.0.0 formal operator release`

Completion audit:

- `future/v4/v4_goal4633_4644_completion_audit_2026-06-25.md`
- `future/v4/v4_goal4646_pretag_wording_fixes_completion_2026-06-25.md`

Goal range completed:

- Goal4633 through Goal4646.

## Verified Release Facts

- V4.0 measured release surfaces: `8`
- V4.0 candidate release surfaces: `0`
- V4.0 deferred/excluded rows: `2`
- public performance wording: most measured operators are 1.2-1.7x against
  their stated baselines; any-hit flags is 5.671x; point-nearest and AABB are
  large scale-dependent algorithmic-complexity wins. Do not headline the raw
  5.185x geomean.
- Claude Goal4644 review verdict:
  `accept_goal4644_post_release_guardrails`
- Clean worktree validation at commit `b8528c67d`:
  - full V4 tests: `179 tests OK`
  - catalog dry-run: `passed`
  - V4 quickstart: `ok`
- Goal4646 local validation:
  - targeted wording/release group: `39 tests OK`
  - full V4 tests: `185 tests OK`
  - catalog dry-run: `passed`, bounded label printed
  - V4 quickstart: `ok`, bounded label printed
- Goal4646 review:
  - Claude verdict: `accept_goal4646_wording_fixes_tag_unblocked`
  - independent Codex verdict: `accept_goal4646_wording_fixes_tag_unblocked`
  - Antigravity: `blocked_empty_output_not_counted_as_review`

The release remains bounded. It does not authorize:

- broad V4 speedup;
- whole-application speedup;
- all-benchmark speedup;
- public true-zero-copy;
- Tier-3 callback support;
- raw OptiX callback support;
- CuPy performance;
- C ABI / embedding / non-Python host bindings;
- app-specific native kernels;
- Barnes-Hut coverage;
- Spatial RayJoin coverage;
- LibRTS paper reproduction.

## Current Workspace Caveat

The clean validation worktree is clean and reproducible. The main worktree still
contains unrelated dirty/untracked artifacts that were not part of the V4.0.0
release commit, including old stderr/pid evidence files, V3 temporary scripts,
and one modified Claude helper script.

These artifacts should not be treated as release blockers, but they should be
cleaned or archived before future development continues heavily in the main
workspace.

## Recommended Next Goals

### Goal4645. Release Hygiene / Tree Cleanup

Purpose:

- clean or archive old temporary stderr, pid, tgz, V3/Phoenix, and blocked-review
  artifacts without deleting release evidence.

Exit gate:

- main worktree is understandable;
- current V4.0 front-door files remain untouched except for documentation of the
  cleanup;
- no required evidence file is lost.

### Goal4646. Release Tag / Distribution Packet

Purpose:

- prepare the public release wrapper around the committed V4.0.0 state.

Status:

- wording/tag gate complete;
- public label corrected to bounded operator wording;
- distribution, denominators, and outlier classes recorded;
- external review accepts the wording fix.

Remaining release-packaging tasks:

- prepare `v4.0.0` tag command/owner approval note;
- prepare final release notes from the corrected wording;
- verify install/quickstart instructions from the committed Goal4646 state.

### Goal4647. V4.1 Planning

Purpose:

- open future work without contaminating V4.0.0 claims.

Candidate V4.x topics:

- CuPy validation;
- more generic operator coverage;
- Tier-3 callback spike;
- C ABI / embedding;
- non-Python host bindings.

Exit gate:

- V4.x goals are separated from V4.0.0 release docs and cannot be mistaken for
  already-supported V4.0 features.

## Recommendation

Do not change the V4.0 performance story now. V4.0 is complete and bounded. The
next correct move is release hygiene, then release packaging, then V4.x planning.
