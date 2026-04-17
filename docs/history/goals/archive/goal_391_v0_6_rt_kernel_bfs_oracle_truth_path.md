# Goal 391: v0.6 RT-Kernel BFS Oracle Truth Path

## Objective

Implement the first bounded native/oracle execution path for the RTDL-kernel
graph line by supporting one BFS expansion step through `rt.run_cpu(...)`.

## Why This Goal Exists

Goals 389-390 proved the corrected RT graph line at the Python truth-path
level:

- RT-kernel `bfs` step in Python
- RT-kernel `triangle_count` step in Python

The next bounded execution step is to prove that the existing native/oracle
runtime can execute the BFS graph step with row parity against the Python
reference.

## Required Outcome

This goal is complete only when the repo contains:

- a narrow native/oracle ABI for bounded BFS expansion
- Python binding/runtime support for `rt.run_cpu(...)` on RT-kernel BFS
- focused parity tests proving `run_cpu(...) == run_cpu_python_reference(...)`
  for bounded BFS graph steps

## Honesty Boundary

This goal does not claim:

- native/oracle support for RT-kernel `triangle_count`
- graph lowering onto Embree, OptiX, or Vulkan
- RT backend execution beyond the existing bounded oracle/native path

This goal is only the bounded native/oracle closure for the RT-kernel BFS
step.
