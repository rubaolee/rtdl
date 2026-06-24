# Goal 533: Codex Review Of RTDL API Brainstorm

Date: 2026-04-18
Reviewer: Codex
Source: `/Users/rl2025/.gemini/antigravity/brain/d81e2ad6-bc5f-4c4b-b49f-0e44b3f64284/rtdl_api_brainstorm.md`
Verdict: **REVISE / BLOCK AS WRITTEN**

## Summary

The brainstorm has a useful technical observation: current ITRE is a
single-pass row-emission model, while low-level RT APIs expose ray lifecycle
stages and mutable ray payloads. That gap is real.

The proposed solution is not acceptable as an RTDL next step because it
reframes RTDL as a rendering/simulation shader language. That conflicts with
the current `v0.8.0` architecture and capability boundary, where RTDL is a
Python-hosted language/runtime for query kernels and Python owns application
orchestration, reductions, visualization, and domain state.

## Major Findings

1. The proposal changes the product category.

   Section 2 says RTDL should evolve into a "Hardware-Accelerated Simulation"
   engine. That is broader than RTDL's released position and conflicts with the
   documented boundary that RTDL is not a renderer, graphics engine, shader
   language, material system, or full simulation framework.

2. Event hooks are shader-stage APIs, not a small ITRE refinement.

   `on_closest_hit`, `on_any_hit`, and `on_miss` would expose an OptiX-style
   shader lifecycle. That is a major new execution model, not an extension of
   the current `refine -> emit rows` contract.

3. Mutable payloads break the current row-emission boundary.

   Payload fields like `radiance`, `attenuation`, `visibility`, and `depth`
   move application state and reductions into the kernel. RTDL currently emits
   rows; Python turns those rows into app answers.

4. Recursive ray enqueuing is not backend-neutral in the current design.

   `rt.enqueue_ray` implies device-side recursion or work queues. That would
   require new semantics and backend lowering for CPU/oracle, Embree, OptiX,
   and Vulkan. It should not be treated as syntax-only API work.

5. Rendering examples are the wrong validation workload.

   Ambient occlusion, path tracing, BRDF scattering, skybox sampling, soft
   shadows, and depth-of-field are graphics/material-system examples. They
   should not drive RTDL language growth unless the project explicitly chooses
   to abandon the current boundary.

## Salvageable Ideas

- Any-hit early termination is worth keeping if reframed as a bounded
  non-graphical query feature, such as line-of-sight or visibility rows.
- The "ITRE versus low-level RT pipeline" gap analysis can be reused as
  background, but only after removing renderer/material examples.
- A narrower future proposal could explore bounded traversal options,
  row-level accumulators, or multi-stage Python-orchestrated kernels for
  non-graphical workloads such as LOS batches, graph expansion, or hierarchical
  candidate generation.

## Recommended Next Step

Do not implement the brainstorm as written.

Rewrite it as a non-rendering design note:

- target workloads: line-of-sight, visibility, multi-hop graph, hierarchical
  candidate filtering, or Barnes-Hut-style candidate levels
- allowed surfaces: traversal options, bounded emitted fields, prepared data,
  and Python-orchestrated multi-kernel flows
- excluded surfaces: shader callbacks, material systems, BRDFs, skyboxes,
  path tracing, global illumination, and recursive device-side ray spawning

The first implementable candidate should be **any-hit early termination for
bounded LOS/visibility queries**, with CPU/oracle correctness first and native
backend acceleration only after the contract is proven.
