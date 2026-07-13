# Goal5120 - X-HD-Style Decision Route Feasibility

Date: 2026-07-08

## Verdict

```text
xhd_style_decision_route_requires_new_generic_api
```

## Purpose

Decide whether RTDL can reproduce the X-HD-style fixed-radius / decision logic
with existing generic primitives, without creating an X-HD-specific primitive.

## Existing RTDL Assets

RTDL already exposes a generic 2D fixed-radius threshold-count primitive:

```text
prepare_generic_fixed_radius_count_threshold_2d(search_points, backend, max_radius)
run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)
```

The existing research benchmark route under
`examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
uses it to express a directed Hausdorff decision subproblem:

```text
for all source points a:
  exists target point b with distance(a, b) <= radius
```

That is exactly the predicate:

```text
directed_hd(source, target) <= radius
```

for a fixed radius.

## What Is Feasible Now

Existing generic RTDL support can express:

- 2D fixed-radius coverage/count decision;
- prepared scene reuse for repeated 2D radius probes;
- scalar threshold count summaries;
- exact 2D and 3D columnar reference routes through public column APIs.

This is useful system functionality, and it is not X-HD-specific.

## What Is Not Feasible As A Complete X-HD Route Yet

The author X-HD `rt/gpu` algorithm is not just one fixed-radius decision. It
performs iterative radius/bounds work and reports X-HD internal phase fields such
as:

```text
HDLowerBound
HDUpperBound
InitRadius
Iterations[*].Radius
Iterations[*].CMax2
Iterations[*].RTTime
Iterations[*].CUDATime
Iterations[*].OffloadingSize
BVHBuildTime
```

Current RTDL public API does not expose a complete generic 3D iterative X-HD
execution contract with:

- repeated radius refinement;
- RT candidate offloading decisions;
- X-HD-equivalent bounds update;
- 3D fixed-radius public prepared query front door comparable to the current 2D
  primitive;
- author-like per-iteration phase accounting.

## Local Execution Note

A local attempt to exercise the 2D prepared fixed-radius route with Embree hit a
Windows/native build/linker blocker (`undefined symbol: __floattidf`). This is
an environment/toolchain blocker for local execution, not evidence that the
generic primitive is semantically invalid. The API and prior tests exist; this
goal is a feasibility decision, not a new native backend bring-up.

## Decision

For v2.14.5 / the current X-HD paper app closeout:

- keep the bounded RTDL route as the public exact columnar 2D/3D route;
- do not claim it is the author X-HD RT-core implementation;
- do not write an X-HD-specific primitive;
- carry forward a future system/API goal if we want true X-HD-style generic
  iterative decision support.

The future generic API, if authorized, should be framed as something like:

```text
generic directed Hausdorff threshold/refinement pipeline
```

not as `xhd_*` or paper-app code.

## Claim Boundary

Authorized:

- existing generic 2D fixed-radius threshold primitive can express a directed
  Hausdorff decision predicate for fixed radius;
- current X-HD paper app has bounded 2D/3D exact columnar routes;
- complete X-HD-style iterative RT route needs additional generic API work.

Not authorized:

- claiming RTDL has reproduced the author X-HD RT-core algorithm;
- claiming X-HD speedup or performance parity;
- adding an X-HD-named core primitive.
