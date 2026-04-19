# Goal 533 — RTDL API Brainstorm Design Review

**Reviewer:** Claude (Sonnet 4.6)
**Date:** 2026-04-18
**Source brainstorm:** `~/.gemini/antigravity/brain/d81e2ad6-bc5f-4c4b-b49f-0e44b3f64284/rtdl_api_brainstorm.md`
**Reference documents:** `docs/current_architecture.md`, `docs/rtdl/itre_app_model.md`, `docs/capability_boundaries.md`

---

## Verdict: BLOCK

The brainstorm cannot be accepted in its current form. Its stated goal — turning RTDL into a
"Hardware-Accelerated Simulation engine" targeting path tracing, global illumination, and ambient
occlusion — directly contradicts every categorical boundary in the v0.8 architecture. The proposal
does not introduce one new workload type; it redefines RTDL as the thing the architecture explicitly
says RTDL must not become: a renderer, a shader language, and a material system.

---

## Major Findings

### 1. The framing is the wrong question

The brainstorm opens from a correct technical observation (ITRE lacks payload state and multi-stage
shader hooks) but then immediately drives toward graphical rendering as the motivating use case.
Every concrete example — path tracing, ambient occlusion, global illumination, BRDFs, skybox
sampling, Depth-of-Field, soft shadows — is a graphics rendering primitive. `docs/current_architecture.md`
is unambiguous:

> Do not read the current system as: a general-purpose renderer.

`docs/capability_boundaries.md` is equally direct in its "cannot become" list:

> RTDL is not intended to become: a renderer, a graphics engine, a shader language, a material
> system, an animation system, a scene editor.

The brainstorm's Section 4 conclusion, "RTDL can break free from the strict relational database
paradigm," is precisely the direction the architecture documents say RTDL should not go. The
relational/query character of ITRE is a feature, not a deficiency.

### 2. Event hooks (`on_closest_hit`, `on_miss`, `on_any_hit`) as proposed are shader stage hooks

The brainstorm replaces ITRE's `Refine` step with SBT-mapped shader stage callbacks. `Refine` in
ITRE is a bounded, typed, backend-dispatchable predicate that turns candidate hits into valid
rows. The proposed hooks are GPU kernel callbacks designed to execute arbitrary material logic,
mutate payload state, spawn rays, and sample environment maps. These are not a generalization of
`Refine`; they are a replacement of the entire ITRE model with an OptiX-style shader pipeline.

This is architecturally incompatible with `itre_app_model.md`, which defines Refine as:

> apply the workload-specific rule that turns broad candidates into valid rows

and with `capability_boundaries.md`:

> RTDL should not grow by hiding complete applications inside special-case primitives.

### 3. Stateful Payloads with rendering fields break the row-emission contract

ITRE emits rows to Python. Python owns reductions. Mutable payloads (fields: `radiance`,
`attenuation`, `Color`) carrying rendering state across bounces collapse the boundary between
RTDL kernel and Python app. The accumulation of radiance across recursive hops is precisely the
kind of reduction that `itre_app_model.md` assigns to Python:

> Python reduces rows and implements domain-specific application logic.

Radiance accumulation is not a row emission; it is stateful multi-bounce rendering. Embedding it
in the RTDL payload moves an application-layer concern permanently into the kernel model.

### 4. Recursive ray enqueuing is incompatible with ITRE's single-pass traversal model

`rt.enqueue_ray()` (with loop condition) is a device-side recursion primitive. ITRE's traversal
is single-pass: one traversal, one emit, Python sees the result. Recursive ray spawning
fundamentally changes the execution model to match OptiX's `optixTrace` recursion semantics. This
would require new runtime guarantees, new termination semantics, and new backend lowering for every
supported backend (cpu_python_reference, cpu/oracle, Embree, OptiX, Vulkan). The brainstorm treats
this as a straightforward DSL addition; it is in practice a new execution engine.

### 5. `rt.math.scatter`, `rt.sample_skybox`, BRDF primitives are material system primitives

A hardware-accelerated math library for microfacet BRDFs, scattering, and skybox sampling is a
material system. `capability_boundaries.md` names "material system" as an explicit "cannot become"
category. These primitives have no non-graphical analogue in the current workload families and
would create language surfaces with zero reuse across the spatial, graph, and DB-style workload
families that RTDL actually supports.

### 6. `RayGen Distributions` conflates probe patterns with rendering sampling strategies

`rt.HemisphereDistribution(samples=32, normal_field="normal")` is an importance-sampling strategy
for rendering. RTDL probe patterns (probe records that generate search geometries) are
conceptually related but fundamentally different: they are typed input records, not sampling
distributions over a hemisphere around a shading normal. Framing this as RTDL language growth
confuses ray generation for spatial queries with ray generation for Monte Carlo rendering.

---

## Acceptable Parts

### Gap analysis in Section 1 is technically accurate

The brainstorm correctly identifies that ITRE abstracts away the shader pipeline and payload state
relative to OptiX/Embree. The description of ITRE as "a relational query engine mapped onto
hardware ray tracing" is accurate and useful as a design framing for future language pressure
analysis. This observation does not justify the proposed direction but is worth preserving as a
neutral technical description.

### Any-hit early termination has a legitimate non-graphical use case

`Any-Hit Termination` for line-of-sight / visibility checks is the one proposed feature with a
plausible path inside RTDL's design intent. The current geometry workload family already includes
`any-hit rows` as a distinct concept (e.g., segment/polygon any-hit rows). An explicit early-exit
mode for LOS-style traversal is a bounded query optimization, not a rendering feature. It could
potentially be expressed as a traversal option on existing geometry kernels rather than as a new
hook type. This is the only concept in the brainstorm worth carrying forward, and only in a
non-graphical framing.

---

## Rejected / Deferred Parts

| Feature | Disposition | Reason |
| --- | --- | --- |
| Stateful Payloads (`rt.Payload`) with rendering fields | **Rejected** | Moves app-layer reduction into the kernel; rendering-specific fields have no RTDL reuse |
| `on_closest_hit` / `on_miss` event hooks | **Rejected** | Replace ITRE Refine with SBT shader callbacks; incompatible with row-emission model |
| Recursive ray enqueuing (`rt.enqueue_ray`) | **Rejected** | Requires a new execution engine; breaks single-pass ITRE traversal contract |
| `rt.math.scatter`, `rt.sample_skybox`, BRDF library | **Rejected** | Material system primitives; explicit "cannot become" category |
| `rt.HemisphereDistribution` / RayGen sampling distributions | **Rejected** | Monte Carlo rendering sampling strategy, not a spatial query probe pattern |
| Path tracing kernel example | **Rejected** | Pure rendering application; outside RTDL's stated scope |
| Ambient occlusion kernel example | **Rejected** | Pure rendering application; outside RTDL's stated scope |
| Any-hit termination for LOS / shadow visibility | **Deferred** | Legitimate non-graphical use case; needs re-framing as a bounded query option, not a shader hook |
| Payload state concept (non-rendering) | **Deferred** | The underlying language pressure (stateful traversal for multi-hop non-graphical workloads) is real and worth separate analysis once rendering framing is removed — e.g., multi-hop graph walk with accumulated state, or Barnes-Hut multi-level candidate filtering |

---

## Recommended Next Step

Do not proceed with any part of the brainstorm as written. The proposal should be fully
re-framed before any implementation planning.

The legitimate language pressure behind this brainstorm is:

> ITRE is a single-pass, stateless row-emitter. Some non-graphical workloads (multi-hop graph
> traversal, hierarchical simulation candidate discovery, LOS checks) create pressure for
> traversal-time state accumulation or early-exit control. What is the minimal, non-rendering
> extension to ITRE that addresses that pressure without reintroducing a full shader pipeline?

A productive follow-on analysis would:

1. Enumerate the **non-graphical** workloads currently handled by Python orchestration (e.g., Barnes-Hut
   multi-level, BFS with accumulated path cost, LOS batch queries) that could benefit from
   richer traversal semantics.
2. For each, describe the minimal language surface change (a new traversal option, a new emit field,
   a bounded accumulation type) that stays within ITRE's row-emission model.
3. Treat any-hit early exit for LOS as the first concrete candidate and propose it as a traversal
   option on existing geometry kernels, with CPU/oracle truth path, before any GPU-side design.
4. Explicitly exclude rendering, material systems, shader hooks, and recursive ray spawning from
   scope in every section header.

The gap analysis from Section 1 of the brainstorm can be reused as background context if the
rendering framing is removed.
