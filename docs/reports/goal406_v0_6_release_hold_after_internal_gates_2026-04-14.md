# Goal 406 Report: v0.6 Release Hold After Internal Gates

Date: 2026-04-14

## Purpose

This goal defines the internal hold state for the corrected RT `v0.6` line
after the internal pre-release gates are packaged and before any release act is
considered.

## Intended hold condition

The corrected RT `v0.6` line should enter hold only after:

- Goal `403` pre-release code and test cleanup is closed with 3-AI consensus
- Goal `404` pre-release doc check is closed with 3-AI consensus
- Goal `405` pre-release flow audit is closed with 3-AI consensus

At that point:

- no further release-forward action is taken automatically
- the version waits for the user's external independent release checks

## Current internal readiness view

### Technical readiness

The corrected RT `v0.6` line now has:

- RT graph design/package goals completed
- backend correctness closure completed
- PostgreSQL-backed all-engine correctness completed
- large-scale performance evidence completed
- final bounded correctness/performance closure packaged

### Pre-release gate readiness

The internal pre-release gates are now packaged as:

- [goal403_v0_6_pre_release_code_and_test_cleanup_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal403_v0_6_pre_release_code_and_test_cleanup_2026-04-14.md)
- [goal404_v0_6_pre_release_doc_check_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal404_v0_6_pre_release_doc_check_2026-04-14.md)
- [goal405_v0_6_pre_release_flow_audit_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal405_v0_6_pre_release_flow_audit_2026-04-14.md)

Current remaining requirement:

- complete the 3-AI review chain for Goals `403-405`

## Residual bounded caveats to carry into hold

The hold state should preserve these caveats explicitly:

- the main Linux benchmark GPU was a GTX 1070 with no RT cores, so OptiX
  results are non-RT-core baselines rather than RTX-class RT-core timings
- Gunrock remains useful only as a BFS baseline from this work; its triangle
  count path was not accepted as trustworthy on the validated host/build
- RTDL graph timings here are bounded workload shapes, while some external
  baselines are broader workloads such as full single-source BFS or whole-graph
  triangle count
- Windows validation in this phase was centered on the Embree path rather than a
  full Windows OptiX/Vulkan validation story

## Hold-state language

When Goals `403-405` are closed, the correct status wording is:

- internally review-complete
- externally pending
- no release act yet

## Goal 406 result

Goal 406 currently supports the bounded conclusion that:

- the corrected RT `v0.6` line is moving toward an internal hold state
- the only remaining required internal work is finishing 3-AI closure for the
  pre-release gates
- after that, the version should pause for the user's external independent
  checks
