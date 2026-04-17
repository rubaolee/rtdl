# Goal 389: v0.6 RT-Kernel BFS Python Truth Path

## Objective

Implement the first bounded executable RTDL-kernel BFS step in the Python
truth-path runtime.

## Why This Goal Exists

Goals 385-388 established:

- the corrected `v0.6` direction
- the RT graph kernel surface
- the RT execution interpretation
- the lowering/runtime contract

The next real coding step is to prove that the RTDL kernel form can execute a
bounded BFS expansion step in the Python truth path.

## Required Outcome

This goal is complete only when the repo contains:

- graph input and predicate surface needed for RT-kernel BFS
- a Python truth-path implementation for one bounded BFS expansion step
- focused tests proving compile plus execution behavior

## Honesty Boundary

This goal does not claim:

- native/oracle RT-kernel BFS parity
- lowering support for graph kernels
- backend execution on Embree, OptiX, or Vulkan

This goal is only the Python truth-path closure for the bounded RT-kernel BFS
step.
