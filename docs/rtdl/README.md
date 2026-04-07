# RTDL Language Docs

This directory is the canonical language-facing documentation for the **current
public RTDL surface**.

That surface should not be read only as a closed workload catalog. RTDL also
supports user-authored programs where RTDL provides the geometry-query core and
Python provides surrounding application logic.

The documents here have different roles and should not overlap heavily.

## Read In This Order

1. [DSL Reference](dsl_reference.md)
   - precise syntax and contract
   - authoritative source for what the language accepts

2. [Programming Guide](programming_guide.md)
   - how to author kernels correctly
   - how to choose inputs, predicates, and execution paths

3. [Workload Cookbook](workload_cookbook.md)
   - copyable workload patterns
   - concrete examples by workload family

4. [Feature Homes](../features/README.md)
   - workload-by-workload usage homes
   - best practices, examples, and limitations per feature

5. [LLM Authoring Guide](llm_authoring_guide.md)
   - agent-facing guidance for generating RTDL code

6. [Release-Facing Examples](../release_facing_examples.md)
   - includes small RTDL-plus-Python application demos

## Current Runtime Surface

The language docs describe a public surface that can currently be used through:

- `rt.run_cpu(...)` as the native C/C++ oracle
- `rt.run_embree(...)` as the controlled CPU backend
- `rt.run_optix(...)` as the controlled GPU backend on supported NVIDIA hosts
- `rt.run_vulkan(...)` on the accepted bounded Linux validation surface, still
  provisional beyond that larger-scale boundary

The language surface is still intentionally narrow, but it is no longer only a
planning or code-generation surface.

Current user-programming note:

- RTDL can already work well as the geometry-query layer inside Python
  applications
- a concrete small example is:
  - [rtdl_lit_ball_demo.py](../../examples/rtdl_lit_ball_demo.py)
- that demo is not a claim that RTDL is a rendering system
