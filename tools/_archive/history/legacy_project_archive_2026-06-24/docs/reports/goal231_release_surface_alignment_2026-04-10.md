# Goal 231 Report: v0.4 Release-Surface Alignment

Date: 2026-04-10
Status: implemented

## Summary

The clean release-prep worktree exposed a stale layer in the `v0.4` release
package:

- the release statement still said `v0.4` did not claim GPU nearest-neighbor
  backend closure
- the audit and tag-preparation docs did not yet preserve the later Goal 228
  heavy benchmark and Goal 229 boundary-fix follow-up as part of the live
  release truth
- the final release handoff hub still mentioned local-only banner/docs-reorg
  work that is not present in the clean release-prep checkout

This goal corrects that package surface.

## Files Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/tag_preparation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md`

## Outcome

The clean worktree's `v0.4` release package now states the real current story:

- nearest-neighbor closure now includes CPU/oracle, Embree, OptiX, and Vulkan
- the heavy Linux benchmark and Goal 229 boundary fix are part of the live
  release evidence
- the package remains pre-tag and still requires explicit user authorization
  before any release action
