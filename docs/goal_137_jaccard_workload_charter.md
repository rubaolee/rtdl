# Goal 137: Pathology Jaccard Workload Charter

## Purpose

Define the first implementation boundary for the Jaccard line proposed in Goal 136.

## Accepted scope

- RTDL may pursue **pathology polygon-set Jaccard**.
- The first primitive is:
  - `polygon_pair_overlap_area_rows`
- The first accepted semantics are:
  - polygon-vs-polygon positive-overlap rows
  - orthogonal polygons only
  - integer-grid vertices only
  - no holes in this first closure claim
  - area interpreted as covered unit image cells

## Not accepted in Goal 137

- generic arbitrary set similarity
- generic continuous polygon overlay support
- full overlay geometry materialization
- immediate Embree/OptiX/Vulkan maturity
- public pathology dataset closure

## Row contract for `polygon_pair_overlap_area_rows`

Each emitted row has:

- `left_polygon_id`
- `right_polygon_id`
- `intersection_area`
- `left_area`
- `right_area`
- `union_area`

Only positive-overlap rows are emitted.

## Why this boundary is honest

- It matches the pathology/image-grid motivation from the old paper better than generic polygon overlay.
- It is implementable now in Python and native CPU/oracle.
- It can be checked against PostGIS for authored orthogonal integer-grid cases.
- It does not pretend RTDL already has general polygon intersection geometry support.

## Goal 138 acceptance target

Goal 138 should close:

- Python reference support
- native CPU/oracle support
- authored example
- focused tests
- authored PostGIS parity on Linux

## Later goals after Goal 138

- Goal 139: public pathology data acquisition and conversion
- Goal 140: `polygon_set_jaccard` closure above the primitive
- Goal 141: Linux large-scale/public-data audit
- Goal 142: docs and generate-only expansion
