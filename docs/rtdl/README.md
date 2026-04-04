# RTDL Language Docs

This directory is the canonical language-facing documentation for the **current
public RTDL surface**.

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

4. [LLM Authoring Guide](llm_authoring_guide.md)
   - agent-facing guidance for generating RTDL code

## Current Runtime Surface

The language docs describe a public surface that can currently be used through:

- `rt.run_cpu(...)` as the native C/C++ oracle
- `rt.run_embree(...)` as the controlled CPU backend
- `rt.run_optix(...)` as the controlled GPU backend on supported NVIDIA hosts
- `rt.run_vulkan(...)` on the accepted bounded Linux validation surface, still
  provisional beyond that larger-scale boundary

The language surface is still intentionally narrow, but it is no longer only a
planning or code-generation surface.
