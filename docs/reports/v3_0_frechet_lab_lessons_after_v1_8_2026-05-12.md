# v3.0 Planning Note: Frechet Lab Lessons After v1.8

Date: 2026-05-12
Status: exploratory planning note
Current roadmap focus: v2.0 Python + partner + RTDL

## Purpose

This note records what the post-v1.8 continuous Frechet distance lab taught us
about RTDL as a Python eDSL and about possible future v3.0 engine-extension
work.

It is not a v2.0 requirement and not a v3.0 commitment. The active roadmap
remains:

```text
v2.0 = protocol first, PyTorch reference first, CuPy conformance alongside it,
       engine absolutely app-agnostic throughout.
```

## Lab Summary

We asked a deliberately open learner question:

> If RTDL+Python is a new programming-language surface for CPUs/GPUs, can a
> user write a ray-tracing-accelerated continuous Frechet distance program that
> can exploit NVIDIA RT cores?

The answer is useful but bounded:

- yes, a learner can write a new Python+RTDL application;
- yes, the app can route generic RT-shaped work through OptiX;
- yes, RTDL+Python can beat pure Python on synthetic cases when candidate
  pruning is strong enough;
- no, this particular Frechet split is not a real speedup against optimized C++
  on real GeoLife trajectories.

The lab produced these evidence reports:

- `docs/reports/goal1771_continuous_frechet_python_rtdl_learner_app_2026-05-12.md`
- `docs/reports/goal1772_continuous_frechet_optix_pod_validation_attempt_2026-05-12.md`
- `docs/reports/goal1773_real_dataset_frechet_cpp_baseline_perf_2026-05-12.md`
- `docs/reports/goal1774_frechet_correctness_and_cpp_continuation_fix_2026-05-12.md`
- `docs/reports/goal1775_frechet_tube_broadphase_sweep_2026-05-12.md`
- `docs/reports/goal1776_frechet_masked_cpp_continuation_2026-05-12.md`

## What Worked

The language model worked. A user-facing app could be authored without adding
Frechet-specific native symbols:

- Python owned app orchestration and continuous Frechet semantics.
- RTDL described generic segment/shape traversal and row emission.
- OptiX executed the claim-sensitive RTDL broadphase path on an RTX A5000.
- The app retained claim boundaries instead of pretending the whole algorithm
  was RT-core accelerated.

This is exactly the v1.8 success condition: Python+RTDL is usable for new
programs while the native engine remains app-agnostic.

## What Failed

The first broadphase was too weak:

- axis-aligned segment boxes produced very dense free-space candidates;
- oriented segment tubes improved geometry modeling;
- candidate expansion helped correctness;
- masked C++ continuation proved the plumbing, but still did not beat C++.

On the GeoLife pair, the final Frechet radius was large enough that most
free-space cells survived. The RTDL broadphase therefore added launch and
orchestration cost without removing enough downstream work.

This is the central lesson: RTDL speedups depend on the primitive matching the
algorithmic bottleneck. Generic any-hit traversal is not automatically the
right primitive for every distance or dynamic-programming problem.

## Primitive Insights

The Frechet lab suggests future engine or standard-library primitives that are
generic enough to consider later, but only after v2.0:

| Possible primitive | Why it matters | App-agnostic wording |
| --- | --- | --- |
| Segment-segment distance threshold | Frechet cells depend on whether two segments can come within radius, not only on segment/shape crossing. | `segment_pair_distance_threshold` |
| Compact candidate mask / bitset emission | Downstream algorithms often need yes/no per cell, not row materialization. | `candidate_mask_emit` |
| Batched fixed-radius threshold decisions | Many real workloads ask many pairwise "within R?" questions; batching amortizes RT setup. | `batched_threshold_decision` |
| Prepared segment-set reuse | Rebuilding or relaunching per radius is expensive. | `prepared_segment_payload` |
| Generic monotone-grid reachability | Frechet is reachability over a monotone free-space grid; this can be described without naming Frechet. | `monotone_grid_reachability` |
| Runtime cost-model fallback | RTDL should know when pruning is too weak and fall back to CPU/C++ continuation. | `adaptive_backend_guard` |

These are not requests to add app-shaped native logic. They are candidate
generic primitives or runtime patterns discovered by a hard learner example.

## v3.0 Extension Insight

The old "PCIe slot" metaphor is too simple. This lab shows that extension
performance is not mainly about letting users inject a shader. The hard part is
the contract around:

- what data layout the shader sees,
- what compact output it returns,
- how that output composes with continuations,
- whether setup cost is amortized,
- whether the runtime can predict when the extension is worth using,
- and whether the result stays portable across OptiX, Vulkan, Apple RT, HIPRT,
  and CPU reference paths.

For v3.0, a better mental model is:

```text
Extension = typed device payload contract
          + backend-specific shader entry contract
          + compact output contract
          + conformance tests
          + cost-model and fallback story
```

Shader injection alone is not enough.

## v2.0 Boundary

This lab should not distract from v2.0.

The correct v2.0 lesson is that partner protocol work must make continuation
boundaries explicit. PyTorch and CuPy partners should be able to validate:

- where RTDL owns traversal,
- where the partner owns tensor/native continuation,
- what data is borrowed or copied,
- what output schema is produced,
- and when backend acceleration is actually claimed.

That partner discipline is a prerequisite for any future v3.0 extension story.
If v2.0 blurs partner continuations with engine internals, v3.0 will inherit a
messy extension boundary.

## Non-Claims

Do not claim:

- continuous Frechet is RT-core accelerated on real datasets;
- generic segment/shape any-hit is sufficient for Frechet acceleration;
- v1.8 automatically unlocks shader plug-ins;
- v3.0 should move ahead of v2.0.

Claim instead:

- v1.8 made it possible to write a new Python+RTDL learner app while keeping the
  native engine app-agnostic;
- the Frechet lab identified missing generic primitive shapes and extension
  contracts;
- v2.0 should remain focused on partner protocol, PyTorch reference, and CuPy
  conformance.

## Review Request

This note should be reviewed independently by at least two distinct AI systems
before it is cited in any roadmap summary. Reviewers should check:

- whether the primitive names are sufficiently app-agnostic;
- whether any v3.0 wording overclaims what v1.8 unlocked;
- whether the v2.0 boundary is strong enough;
- whether the Frechet lab evidence supports the conclusions;
- and whether additional non-claims are needed.
