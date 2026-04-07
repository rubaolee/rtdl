# RTDL Feature Guide

This is the **high-level orientation guide** for RTDL.

Audience:

- readers who want a fast overview of what RTDL currently is
- people deciding whether the current system fits their use case
- reviewers who need the feature surface without reading the full language docs

This guide is intentionally lighter than the documents in `docs/rtdl/`.

## What RTDL Is Today

RTDL is a Python-hosted DSL for non-graphical ray-tracing-style workloads.

Today it includes:

- a kernel authoring surface
- compiler IR and lowering
- a native C/C++ oracle
- a controlled Embree backend
- a controlled OptiX backend
- a Vulkan backend that is now hardware-validated and parity-clean on the
  accepted long exact-source `county_zipcode` positive-hit `pip` surface, but
  slower than PostGIS, OptiX, and Embree there

Current supported workload families:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `point_nearest_segment`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Current workload-maturity note:

- `segment_polygon_hitcount` is the first v0.2 workload-family expansion now
  closed beyond the v0.1 RayJoin-heavy slice
- its current accepted closure target is semantic/backend closure across:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  on deterministic authored / fixture / derived cases
- this family must still be described honestly under the current audited local
  `native_loop` boundary rather than as proof of BVH- or RT-core-matured
  traversal
- the family now also has:
  - prepared-path performance characterization
  - large deterministic PostGIS-backed correctness validation on:
    - `cpu`
    - `embree`
    - `optix`
  through the accepted `derived/br_county_subset_segment_polygon_tiled_x256`
  case
- `segment_polygon_anyhit_rows` is the second closed v0.2 segment/polygon family
- the Jaccard line is now real, but only under the narrow pathology/unit-cell
  contract:
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`

Canonical workload homes:

- [Release-Facing Examples](/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md)
- [Feature Homes](/Users/rl2025/rtdl_python_only/docs/features/README.md)

## What RTDL Can Currently Do

The current repo can:

- author kernels in a constrained Python DSL
- compile and lower them
- run them through the native oracle
- run them on Embree
- run accepted long exact-source `county_zipcode` positive-hit `pip` workloads
  on OptiX and Embree with exact parity and accepted performance wins against
  PostGIS on the prepared/repeated boundaries
- run the current narrow Jaccard line on Python/native CPU with PostGIS-backed
  checking on accepted packages
- run the current narrow Jaccard line through the public `embree`, `optix`,
  and `vulkan` surfaces on Linux under documented native CPU/oracle fallback
- run the accepted long exact-source Vulkan surface with exact parity, while
  keeping Vulkan as the slower portable backend
- compare accepted workloads against indexed PostGIS ground-truth queries on the Linux host
- close bounded four-system checks across PostGIS, native oracle, Embree, and OptiX on accepted packages
- support a RayJoin-oriented experiment/reporting workflow
- preserve a bounded accepted v0.1 reproduction package as the current trust anchor

## What RTDL Cannot Yet Claim

RTDL does not yet claim:

- exact computational geometry
- a finished generalized multi-backend optimizer
- full paper-identical reproduction of every RayJoin dataset family
- high-precision native GPU geometry on Vulkan (the accepted bounded path still
  relies on float32 traversal plus exact host-side final truth)
- that every backend/workload/boundary combination is equally mature
- full polygon overlay materialization (`overlay` is still a seed analogue)
- generic continuous polygon Jaccard or generic continuous overlap-area closure
- native Embree/OptiX/Vulkan Jaccard maturity
