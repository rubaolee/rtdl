# RTDL Performance Model

This page explains how to read performance results for the current v2.x-facing
RTDL surface. It is intentionally stricter than marketing language: selecting a
backend, running native code, and publishing a speedup claim are different
things.

## Short Version

RTDL can improve performance when the hot work is inside a prepared backend path
and the comparison uses the same contract. RTDL can be slower when the app
returns large Python row tables, when setup dominates, or when most work happens
after traversal.

The current model is:

- Python is the authoring and control plane.
- RTDL describes traversal, refinement, row emission, and supported reductions.
- Native backends must remain app-agnostic.
- Partner libraries such as NumPy, PyTorch, and CuPy can own tensor-side
  continuation when the app needs GPU or vectorized compute.
- Convenience row output is useful for learning and debugging, but it is not
  always the serious performance path.
- Public speedup wording requires exact evidence for the exact measured
  contract.

Older performance history is preserved in the audit archive, but the learner
model should be read from this current page.

## Timing Boundaries

RTDL performance evidence must name the boundary being timed and the artifact
that records it.

| Boundary | What it means | How to read it |
| --- | --- | --- |
| Python dict rows | End-to-end convenience output with Python materialization | Good for usability; often not the fastest path |
| Raw rows / thin views | Native result buffers exposed with less Python rematerialization | Better measure of backend execution plus thin host overhead |
| Prepared execution | Build-side data and/or rays are reused | Best for repeated-query workloads |
| Compact/native summary | Backend or partner continuation returns reduced output | Useful when users do not need full witness rows |
| Streaming witness output | Bounded pages or columns of witness data rather than one huge Python table | Best when correctness needs witnesses but full materialization would dominate |
| Whole app | Data construction, RTDL execution, partner work, post-processing, and output | Only claim this when the evidence explicitly covers it |

## NVIDIA RT Claim Boundary

For NVIDIA paths, distinguish four levels:

1. `--backend optix` selected an OptiX-capable path.
2. Native OptiX traversal ran for the selected mode.
3. `--require-rt-core` was accepted for a documented bounded path.
4. Same-contract evidence and review authorize public speedup wording.

Only level 4 is a public speedup claim.

Current public wording is governed by:

- [Current Support Matrix](current_main_support_matrix.md)
- [Backend Maturity](backend_maturity.md)
- [v2.3 Release Package](release_reports/v2_3/README.md)
- [v2.3 Release Package](release_reports/v2_3/README.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- `rtdsl.rtx_public_wording_matrix()`

## Why Fast Backends Can Still Look Slow

The convenience path has overhead:

- Python object creation
- input normalization
- `ctypes` marshaling
- result rematerialization into dictionaries
- repeated validation and dispatch
- partner array conversion when a run cannot stay on one memory path

Use [Runtime Overhead Architecture](runtime_overhead_architecture.md) for the
mechanical breakdown. The recurring lesson is simple: returning full Python
objects can dominate a run even when traversal is fast.

## When OptiX Is Slower Than Embree

Embree is a ray-tracing/BVH backend, not a plain Python baseline. A slower
OptiX result is useful engineering evidence when the same-contract comparison is
clean and the bottleneck is identified, but it does not authorize positive
public RT-core wording.

Use slower-than-Embree results to decide the next architecture step:

- if native traversal is fast but setup, packing, launch overhead, or Python
  output dominates, improve the handoff/output contract;
- if native traversal itself is slower, tune the backend layout or narrow the
  claim boundary;
- if parity or same-contract timing is incomplete, keep the result out of
  release claims;
- if the app needs ranking, clustering, graph analytics, exact geometry, or
  SQL-style materialization after traversal, route that work through the Python
  app layer or a partner continuation instead of hardcoding it into the engine.

## Partner Continuation Rule

v2.x treats partner compute as part of the user-visible programming model:

```text
Python owns the app.
RTDL owns app-agnostic RT-shaped traversal.
The partner owns tensor/vector/GPU continuation when the app asks for it.
```

That means a v2.x app may use NumPy, PyTorch, CuPy, or user-controlled extension
code around RTDL. Those choices can be valid app implementations, but public
claims must say exactly which layer produced the speedup.

## Public Wording Rule

Use this template:

```text
RTDL accelerates <exact prepared/native or partner-continuation sub-path> for
<app/workload> under <backend/mode>, with <evidence/report>. This is not a
whole-app speedup claim and does not include <excluded phases>.
```

Do not write:

```text
RTDL accelerates every whole app.
OptiX means RT cores made the app faster.
All graph/DB/polygon workloads are faster with RT.
```
