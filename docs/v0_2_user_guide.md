# RTDL v0.2 User Guide

## What Is New

RTDL v0.2 expands the system beyond the archived v0.1 RayJoin-heavy slice.
This is the released v0.2.0 user-facing scope.

The accepted real v0.2 surface is exactly:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only workflow
- the feature-home documentation layer
- Linux-backed correctness/performance evidence
- the Linux-primary / Mac-limited platform split
- explicit fallback-vs-native backend honesty boundaries

Within that frozen surface:

- the first two items are the closed segment/polygon families
- the last two items are the narrow pathology-style Jaccard line
- public Linux wrapper-surface access to that Jaccard line through:
  - `embree`
  - `optix`
  - `vulkan`
  under documented native CPU/oracle fallback
- a narrow generate-only workflow that now covers both families
- stronger Linux/PostGIS-backed correctness and performance evidence for those
  families

Canonical workload-by-workload homes:

- [Release-Facing Examples](release_facing_examples.md)
- [Feature Homes](features/README.md)

The important boundary is that v0.2.0 is broader and stronger than v0.1, but it
is still not claiming that every backend/workload path is equally mature.

## Workloads

The two main v0.2 workload families are:

### `segment_polygon_hitcount`

Meaning:

- probe side: segments
- build side: polygons
- output: one row per segment with `hit_count`

This is useful when downstream code wants:

- screening
- ranking
- compact per-segment summaries

Example:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def road_hazard_counts():
    roads = rt.input("roads", rt.Segments, role="probe")
    hazards = rt.input("hazards", rt.Polygons, role="build")
    candidates = rt.traverse(roads, hazards, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])
```

### `segment_polygon_anyhit_rows`

Meaning:

- probe side: segments
- build side: polygons
- output: one `(segment_id, polygon_id)` row per true hit

This is useful when downstream code wants:

- exact touched polygon ids
- join-style auditing
- custom aggregation outside RTDL

Example:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def road_polygon_hits():
    roads = rt.input("roads", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(roads, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])
```

### `polygon_set_jaccard`

Meaning:

- probe side: left polygon set
- build side: right polygon set
- output: one aggregate row with:
  - `intersection_area`
  - `left_area`
  - `right_area`
  - `union_area`
  - `jaccard_similarity`

Important boundary:

- this is currently a narrow pathology-style workload
- polygons must fit the orthogonal integer-grid unit-cell contract
- this is not generic continuous polygon-set Jaccard

Example:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_set_similarity():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    rows = rt.refine(candidates, predicate=rt.polygon_set_jaccard(exact=False))
    return rt.emit(
        rows,
        fields=["intersection_area", "left_area", "right_area", "union_area", "jaccard_similarity"],
    )
```

## Generate-Only

RTDL v0.2 keeps a narrow generate-only mode.

That mode is useful when you want:

- a runnable RTDL Python artifact
- a handoff bundle for another developer or reviewer
- explicit verification scaffolding

The current generate-only line is intentionally small:

- it supports the two current v0.2 segment/polygon families
- it also supports one narrow Jaccard entry:
  - authored `polygon_set_jaccard`
- it emits accepted runnable Python artifacts
- it does not claim broad general code generation

## Platforms

Platform status is intentionally explicit.

### Primary platform

Linux is the primary v0.2 development and validation platform for:

- PostGIS-backed correctness
- large deterministic performance runs
- OptiX
- Vulkan

### Local support platform

This Mac is a limited local platform for:

- Python reference
- C/oracle
- Embree

It is not the main validation platform for:

- OptiX
- Vulkan
- Linux/PostGIS large-row evidence

## Backend Notes

### CPU

- trusted practical fallback
- strong on the current large deterministic segment/polygon rows after the
  candidate-index redesign

### Embree

- strong CPU baseline
- prepared reuse is supported on the current segment/polygon families
- performs well on the accepted Linux large rows
- for the narrow Jaccard line, the public `run_embree(...)` surface is accepted
  through documented native CPU/oracle fallback, not an Embree-native Jaccard
  kernel

### OptiX

- strong Linux backend on the current segment/polygon families
- current wins come from the accepted candidate-reduction design and backend
  alignment work
- this is not the same as claiming universal RT-core-native maturity for every
  future workload
- for the narrow Jaccard line, the public `run_optix(...)` surface is accepted
  through documented native CPU/oracle fallback, not an OptiX-native Jaccard
  kernel

### Vulkan

- correctness/portability backend
- must work
- must not be very slow
- currently competitive on the accepted Linux large rows for the two
  segment/polygon families
- not treated as the fully optimized flagship backend
- for the narrow Jaccard line, the public `run_vulkan(...)` surface is accepted
  through documented native CPU/oracle fallback, not a Vulkan-native Jaccard
  kernel

## Quick Start

If you want the easiest path:

1. run `examples/rtdl_hello_world.py`
2. run one release-facing example with `cpu_python_reference`
3. then switch backends deliberately

Repository-root commands:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

The `PYTHONPATH=src:.` prefix tells Python to import the local RTDL package
from this checkout.

Then move to the workload examples below.

Run the v0.2 hitcount example:

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

Run the v0.2 any-hit example:

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

Run the narrow Jaccard example:

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py
```

Generate a runnable handoff artifact:

```bash
PYTHONPATH=src:. python3 scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle
```

For app-style usage, start here:

- [rtdl_road_hazard_screening.py](../examples/rtdl_road_hazard_screening.py)

## RTDL Plus Python Applications

RTDL should not be understood only as a fixed list of named workloads. The
current built-in workload surfaces are important, but users can also build
their own applications by combining RTDL kernels with ordinary Python logic.

That model already works well in the repo today:

- RTDL handles the geometry-query core
- Python handles grouping, filtering, summaries, reports, and visual output

The clearest small example is:

- [rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)

That demo uses RTDL to compute ray/triangle hit relationships and then uses
Python to compute brightness and write a real `.pgm` image. This is an example
of RTDL working well as part of a Python application, not a claim that v0.2.0
is a full graphics/rendering system.

For per-feature usage guidance, best practices, and limitations, use:

- [Release-Facing Examples](release_facing_examples.md)
- [Feature Homes](features/README.md)

## Current Limits

RTDL v0.2 does not currently claim:

- exact computational geometry
- full overlay materialization
- universal backend maturity across every workload
- broad general-purpose code generation
- native AMD/Intel GPU backend maturity without hardware-backed validation

The strongest current v0.2 claim is narrower and more honest:

- two segment/polygon workload families are real
- they are validated strongly on Linux/PostGIS
- they have a narrow generate-only product line
- the Jaccard line is now real, but only on the explicitly narrow pathology/unit-cell contract
- the Jaccard line also has public Linux wrapper-surface consistency on
  `embree`, `optix`, and `vulkan`, but that is not native backend maturity
