# ITRE App Programming Model

ITRE means:

1. **Input**: declare the app data that should enter the RTDL kernel.
2. **Traverse**: map the expensive search/candidate-generation step to a
   ray-tracing-style traversal.
3. **Refine**: apply the workload-specific rule that turns broad candidates
   into valid rows.
4. **Emit**: return stable rows to Python.

This is the core RTDL programming model. The current `v0.8` app-building line
shows that ITRE is enough for the RTDL-owned kernel part of the target apps,
while Python remains the surrounding application language.

## The Honest Claim

RTDL does **not** claim that ITRE alone is a complete application language.

RTDL does claim that ITRE is a useful kernel model for the expensive
query/traversal part of apps that can be decomposed into:

- structured inputs
- candidate search or intersection traversal
- exact bounded refinement
- row emission
- Python-side orchestration and reduction

The intended app shape is:

```text
Python prepares data
  -> RTDL ITRE kernel emits rows
  -> Python reduces rows into the app answer
```

This is a language/runtime boundary, not a weakness. RTDL should reduce the
burden of writing modern ray-tracing workloads; it should not replace Python as
the general app layer.

## What RTDL Owns

RTDL owns the heavy query kernel:

- typed kernel inputs
- probe/build roles
- traversal intent
- backend dispatch
- candidate generation
- hit/refinement semantics inside the bounded workload contract
- emitted row schema
- backend-specific execution on CPU/oracle, Embree, OptiX, and Vulkan where
  supported

## What Python Owns

Python owns the app:

- loading and shaping domain data
- building fixtures, trees, graphs, tables, or pose batches
- multi-step orchestration
- app control flow and iteration
- reductions that are not yet RTDL primitives
- visualization and file output
- comparison against app-level or external baselines

The performance target is that Python should not do the heavy traversal or
candidate-search work when a supported RTDL backend can do it. Python can still
own lightweight orchestration and reductions.

## v0.8 App Mapping

| App | ITRE-covered RTDL core | Python-owned app logic |
| --- | --- | --- |
| Hausdorff distance | point-set inputs become nearest-neighbor rows | reduce nearest-neighbor rows into directed/undirected Hausdorff distance and witness IDs |
| Robot collision screening | link edge rays traverse obstacle triangles and emit hit-count rows | build poses/link rays, group hits into pose collision flags |
| Barnes-Hut force approximation | body and node inputs become candidate interaction rows | build the quadtree, apply opening policy, compute vector forces and oracle error |

## App-Specific Readout

### Hausdorff Distance

ITRE is enough for the RTDL-owned part because the heavy operation is nearest
neighbor search:

- Input: two point sets.
- Traverse: query points against search points.
- Refine: bounded nearest-neighbor selection.
- Emit: nearest-neighbor rows.
- Python: max-distance reduction and witness reporting.

### Robot Collision Screening

ITRE is enough for the RTDL-owned part because the heavy operation is
ray/triangle hit counting:

- Input: robot link edge rays and obstacle triangles.
- Traverse: rays through triangle geometry.
- Refine: valid hit intervals and hit-count semantics.
- Emit: per-edge hit-count rows.
- Python: pose construction, link metadata, and collision flag aggregation.

### Barnes-Hut Force Approximation

ITRE is only enough for the first bounded candidate-generation part:

- Input: bodies and Python-built quadtree nodes.
- Traverse: body probes against node candidates.
- Refine: bounded candidate filtering.
- Emit: body-to-node candidate rows.
- Python: tree construction, opening rule, vector force accumulation, exact
  fallback, and error reporting.

This is why Barnes-Hut is the strongest v0.8 language-pressure example. If RTDL
later targets fuller hierarchical simulation kernels, likely language growth
areas are:

- tree-node input types
- opening predicates
- grouped vector reductions
- iterative multi-stage kernel orchestration

## What This Does Not Prove

The v0.8 apps do not prove that:

- RTDL is a full app language.
- RTDL replaces Python.
- every paper workload can be implemented without new primitives.
- ITRE handles arbitrary control flow or arbitrary reductions.
- every backend is faster for every app.

The evidence supports the narrower claim:

**ITRE is sufficient for the RTDL-owned query/traversal kernels in the current
v0.8 target apps, when Python owns orchestration and app-level reductions.**

