# Goal 95 Report: v0.1 Release Docs

Date: 2026-04-05
Status: complete

## Objective

Create the release-facing documentation needed to understand RTDL v0.1 without
reconstructing the project from scattered goal reports.

## New release-facing docs

Added:

- `/Users/rl2025/rtdl_python_only/docs/v0_1_release_notes.md`
- `/Users/rl2025/rtdl_python_only/docs/v0_1_reproduction_and_verification.md`
- `/Users/rl2025/rtdl_python_only/docs/v0_1_support_matrix.md`

These now provide:

- the release summary
- the reviewer/reproduction path
- the backend/workload/boundary support matrix

## Live doc refresh

Updated:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/v0_1_final_plan.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/rayjoin_target.md`

Main corrections:

- the repo no longer presents only the older bounded-package story
- the live docs now also reflect the newer long exact-source backend closure
- the bounded package remains the trust anchor
- OptiX and Embree are described as the current mature performance backends
- Vulkan is described as supported and parity-clean, but slower

## Outcome

Goal 95 closes the release-doc gap identified by the milestone audit:

- there is now a release-facing front door
- release readers no longer need to infer status from many goal reports
- the strongest current claim surface and the bounded trust anchor now coexist
  coherently in the live docs
