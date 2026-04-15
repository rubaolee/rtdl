# Goal 390: v0.6 RT-Kernel Triangle Count Python Truth Path

## Objective

Implement the first bounded executable RTDL-kernel triangle-count step in the
Python truth-path runtime.

## Why This Goal Exists

Goal 389 established the first executable RTDL graph-kernel BFS slice.

To complete the opening bounded graph pair for the corrected `v0.6` line, the
repo also needs a Python truth-path step for:

- `triangle_count`

using the RTDL kernel surface rather than detached helper APIs.

## Required Outcome

This goal is complete only when the repo contains:

- graph seed input support needed for triangle-count kernels
- a Python truth-path implementation for one bounded triangle-count probe step
- focused tests proving compile plus execution behavior

## Honesty Boundary

This goal does not claim:

- native/oracle RT-kernel triangle parity
- graph lowering support
- backend execution on Embree, OptiX, or Vulkan

This goal is only the Python truth-path closure for the bounded RT-kernel
triangle-count step.
