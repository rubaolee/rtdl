# Goal 392: v0.6 RT-Kernel Triangle Oracle Truth Path

## Objective

Implement the bounded native/oracle execution path for the RTDL-kernel
triangle-count step so `rt.run_cpu(...)` supports `triangle_match(...)` with
row parity against the Python reference.

## Why This Goal Exists

Goal 391 established the first bounded native/oracle graph execution step for
RT-kernel BFS. The next symmetric dependency is the bounded native/oracle graph
step for RT-kernel triangle probing.

## Required Outcome

This goal is complete only when the repo contains:

- a narrow native/oracle ABI for bounded triangle probing
- Python binding/runtime support for `rt.run_cpu(...)` on RT-kernel
  `triangle_match(...)`
- focused parity tests proving `run_cpu(...) == run_cpu_python_reference(...)`
  for bounded triangle graph steps

## Honesty Boundary

This goal does not claim:

- graph lowering
- Embree, OptiX, or Vulkan graph execution
- large-scale backend performance results

This goal is only the bounded native/oracle closure for the RT-kernel
triangle-count step.
