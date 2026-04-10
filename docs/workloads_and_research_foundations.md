# RTDL Workloads And Research Foundations

This page explains two things:

1. which workload families RTDL currently supports
2. which research papers motivate those workloads and future workload
   directions

The purpose is to make the project surface look intentional and research-backed
rather than ad hoc.

## Reading Rule

- a workload may be **supported now**
- a workload may be **planned / research-backed**
- a paper can motivate a workload family even if that exact workload is not yet
  released in RTDL

So this page separates:

- current implementation status
- research foundation

## Current Supported Workloads

### Released v0.2.0 workload surface

These are the accepted public workloads in the released `v0.2.0` package:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

### Active v0.4 preview workload surface

These are implemented in the active nearest-neighbor preview line, but are not
released yet:

- `fixed_radius_neighbors`
- `knn_rows`

### Additional implemented workload families in the broader codebase

These exist in the repo as real workload/runtime families, but they are not all
part of the current released headline surface:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `point_nearest_segment`

## Workload To Paper Mapping

### `lsi`, `pip`, `overlay`

Primary foundation:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)

Why it matters:

- RayJoin is the first direct application target for RTDL
- it gives the project a concrete non-graphical spatial-join problem
- the current RTDL spatial workload line was initially shaped around this paper

### `segment_polygon_hitcount`, `segment_polygon_anyhit_rows`

Primary foundation:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)

Why it matters:

- these workloads are RTDL’s bounded release-facing segment/polygon evolution
  from the original spatial-join problem
- they stay in the same non-graphical ray-tracing-for-spatial-computation lane

### `point_nearest_segment`

Primary foundation:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)

Why it matters:

- this is a natural adjacency workload in the same spatial-query family
- it helps expand RTDL beyond join-only surfaces while staying consistent with
  the project’s original spatial-data focus

### `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`

Current status:

- supported now under a narrower pathology/unit-cell boundary

Research relationship:

- this line is currently justified more by bounded workload-design extension
  from RTDL’s spatial-query program than by one single canonical paper in the
  repo
- it should therefore be read as **research-adjacent**, but not yet as the same
  kind of direct paper reproduction target that RayJoin is

### `fixed_radius_neighbors`, `knn_rows`

Primary foundation:

- Jianqiao Sun, Yao Zhang, Minsong Wei, and Xiaoyong Du,
  *RTNN: Accelerating Nearest Neighbor Search with Ray Tracing*,
  Proceedings of the 2022 ACM SIGMOD/PODS International Conference on
  Management of Data (SIGMOD 2022),
  DOI: [10.1145/3503221.3508409](https://doi.org/10.1145/3503221.3508409)

Why it matters:

- this is the main direct research foundation for the active `v0.4`
  nearest-neighbor line
- it supports the choice to make nearest-neighbor search the next core
  non-graphical workload family after `v0.3.0`

### Hausdorff-distance direction

Not supported yet as a public RTDL workload, but directly relevant as a future
research-backed direction:

- Liang Geng, Zhehu Yuan, Rubao Lee, Fusheng Wang, and Xiaodong Zhang,
  *X-HD: Fast Hausdorff Distance Computation with Ray Tracing*,
  Proceedings of the 39th ACM International Conference on Supercomputing
  (ICS 2026),
  DOI: not listed in the current public materials yet

Why it matters:

- it gives RTDL a research-backed direction beyond nearest-neighbor search
- it shows that future workload growth can remain non-graphical and geometry-heavy

## Broader System Papers Behind The Direction

These papers are not one-to-one workload definitions, but they explain why RTDL
is framed as a broader ray-tracing-enabled data/runtime system:

- Yangming Lv, Kai Zhang, Ziming Wang, Xiaodong Zhang, Rubao Lee, Zhenying He,
  Yinan Jing, and X. Sean Wang,
  *RTScan: Efficient Scan with Ray Tracing Cores*,
  Proceedings of the VLDB Endowment 17(6), 1460--1472, 2024,
  DOI: [10.14778/3648160.3648183](https://doi.org/10.14778/3648160.3648183)

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *LibRTS: A Spatial Indexing Library by Ray Tracing*,
  Proceedings of the 30th ACM SIGPLAN Annual Symposium on Principles and
  Practice of Parallel Programming (PPoPP 2025),
  DOI: [10.1145/3710848.3710850](https://dl.acm.org/doi/10.1145/3710848.3710850)

- Xuri Shi, Kai Zhang, X. Sean Wang, Xiaodong Zhang, and Rubao Lee,
  *RayDB: Building Databases with Ray Tracing Cores*,
  Proceedings of the VLDB Endowment 19(1), 43--55, 2025,
  DOI: [10.14778/3772181.3772185](https://doi.org/10.14778/3772181.3772185)

These matter because they show that RTDL is part of a coherent research line:

- spatial join
- scan
- spatial indexing/runtime systems
- database systems with ray-tracing cores

## Honest Summary

- RTDL’s earliest and strongest workload foundation is RayJoin
- the active `v0.4` line is founded on nearest-neighbor research rather than
  an ad hoc feature choice
- some current workloads, especially the narrow Jaccard line, are real and
  useful but are not yet tied here to a single canonical workload paper in the
  same direct way
- the project’s workload growth should keep following named research targets,
  not arbitrary feature accumulation
