# Goal 407 Report: v0.6.1 Release Decision

Date: 2026-04-15

## Decision

RELEASE

## Basis

The corrected RT `v0.6` line now has:

- final bounded correctness/performance closure
- internal 3-AI pre-release closure for Goals `403-406`
- external independent release check with verdict `ACCEPT`

External independent review:

- [external_independent_release_check_review_2026-04-15.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/external_independent_release_check_review_2026-04-15.md)

## Version identifier

The corrected RT release will be published as:

- `v0.6.1`

Reason:

- `v0.6.0` is already occupied by the earlier mis-scoped line and should remain
  a historical artifact rather than be silently overwritten.

## Release statement

The corrected RT `v0.6.1` line is accepted for release as:

- an RTDL-kernel graph release
- with bounded correctness closure
- with PostgreSQL-backed correctness anchor
- with performance evidence on real public datasets
- with OptiX and Vulkan as the main RTDL graph backends going forward
