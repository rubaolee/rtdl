# Goal 382 Report: v0.6 release-make state

## Summary

The release-facing repo state now matches a released `v0.6.0` package.

The front door, docs index, and `v0.6` release package now consistently state:
- current released version: `v0.6.0`
- bounded graph workloads added in this release:
  - `bfs`
  - `triangle_count`
- Linux-primary graph evaluation story
- Python/oracle/PostgreSQL bounded graph runtime/baseline story

## What changed

The release-facing package was promoted from release-prep language to released
state:

- `docs/release_reports/v0_6/README.md`
- `docs/release_reports/v0_6/release_statement.md`
- `docs/release_reports/v0_6/support_matrix.md`
- `docs/release_reports/v0_6/audit_report.md`
- `docs/release_reports/v0_6/tag_preparation.md`

The repo front door and docs index were also aligned:

- `README.md`
- `docs/README.md`

## External release-state judgment

External review now says the repo content is ready for tagging:
- [gemini_goal382_v0_6_release_make_state_review_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal382_v0_6_release_make_state_review_2026-04-14.md)

## Effect

The only remaining step after Goal 382 is the actual Git release act:
- stage
- commit
- tag `v0.6.0`
- push
