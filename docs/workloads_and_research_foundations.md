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

It is intentionally narrower than the full repo history:

- it lists the public/current workload families and the main papers that justify
  them
- it does not try to restate every archived planning or review artifact

## Current Supported Workloads

### Released v0.2.0 workload surface

These are the accepted public workloads in the released `v0.2.0` package:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

### Active v0.4 preview workload surface

These are implemented in the active nearest-neighbor preview line (currently running across CPU/Oracle, Embree, OptiX, and Vulkan backends), but are not released yet:

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

`ray_tri_hitcount` is included here as a real low-level primitive workload in
the repo, but not as a front-door named paper-reproduction target in the same
way as the RayJoin and RTNN lines.

## Workload To Paper Mapping

### RayJoin-centered spatial workloads

Workloads:

- `lsi`
- `pip`
- `overlay`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`

Primary foundation:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://doi.org/10.1145/3650200.3656610)

Why it matters:

- RayJoin is the first direct application target for RTDL
- it gives the project a concrete non-graphical spatial-join problem
- the current RTDL spatial workload line was initially shaped around this paper
- these workloads are the RayJoin-derived and RayJoin-adjacent spatial-query
  family in RTDL
- some of them are closer to direct paper reproduction targets than others, but
  they all belong to the same non-graphical spatial-data lane

### `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`

Primary foundation:

- Kaibo Wang, Yin Huai, Rubao Lee, Fusheng Wang, Xiaodong Zhang, and Joel H.
  Saltz,
  *Accelerating Pathology Image Data Cross-Comparison on CPU-GPU Hybrid Systems*,
  Proceedings of the VLDB Endowment 5(11), 1543--1554, 2012,
  DOI: [10.14778/2350229.2350268](https://doi.org/10.14778/2350229.2350268)

Why it matters:

- this paper is the right historical anchor for RTDL's overlap-area and Jaccard
  similarity line
- it is explicitly about large-scale spatial cross-comparison in pathology
  imaging
- the workload center of that paper is computing intersection/union behavior on
  polygon sets and using Jaccard similarity as the comparison measure
- RTDL's `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` are the
  direct bounded descendants of that overlap/similarity lane, even though the
  current RTDL surface is packaged as reusable language workloads rather than as
  the original pathology application pipeline

### `fixed_radius_neighbors`, `knn_rows`

Primary foundation:

- Yuhao Zhu,
  *RTNN: Accelerating Neighbor Search Using Hardware Ray Tracing*,
  Proceedings of the 27th ACM SIGPLAN Annual Symposium on Principles and
  Practice of Parallel Programming (PPoPP '22),
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
  DOI: not yet available in the current public materials (ICS 2026 proceedings)

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
  DOI: [10.1145/3710848.3710850](https://doi.org/10.1145/3710848.3710850)

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
- the overlap-area and Jaccard line now has a named pathology-image
  cross-comparison paper anchor rather than only a loose research association
- the project’s workload growth should keep following named research targets,
  not arbitrary feature accumulation
