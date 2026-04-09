# Goal 191 Report: v0.3 Comprehensive Verification

## Outcome

Planned.

This goal is the final comprehensive pre-release verification sweep for the `v0.3`
line. It should be executed after the current structural cleanup goals are closed and
before release packaging.

## Planned Verification Shape

- run a bounded verification slice across the early RTDL workload line
- run backend/runtime slices across CPU/oracle, Embree, OptiX, and Vulkan where available
- run bounded direct checks for the `examples/visual_demo/` programs
- generate only small supporting video artifacts where they materially verify the current path
- avoid long Windows HD rerenders

## Required Deliverables

- executed command list
- pass / skip / fail accounting
- blocker list if anything fails
- final closure review under:
  - Codex
  - Claude
  - Gemini
