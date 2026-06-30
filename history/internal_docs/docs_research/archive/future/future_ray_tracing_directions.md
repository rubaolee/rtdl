# Future Ray-Tracing Directions

This page collects the most relevant ray-tracing research directions that help
explain where RTDL can go after v0.1.

## Why this page exists

RTDL v0.1 is centered on RayJoin-style spatial work, but the larger research
direction is broader: non-graphical workloads that can benefit from
ray-tracing hardware and traversal software.

The papers below are useful because they show where that larger direction is
already going.

## Papers from the current project line

These are the main ray-tracing-related papers currently listed on Rubao Lee's
homepage, ordered by time.

Copyright belongs to the respective authors and publishers.

### 2024: RayJoin

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  [*RayJoin: Fast and Precise Spatial Join*](https://dl.acm.org/doi/10.1145/3650200.3656610),
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)

Why it matters here:

- this is the direct motivating workload family for RTDL v0.1

### 2024: RTScan

- Yangming Lv, Kai Zhang, Ziming Wang, Xiaodong Zhang, Rubao Lee, Zhenying He,
  Yinan Jing, and X. Sean Wang,
  [*RTScan: Efficient Scan with Ray Tracing Cores*](https://www.vldb.org/pvldb/vol17/p1460-lv.pdf),
  Proceedings of the VLDB Endowment 17(6), 1460--1472, 2024,
  DOI: [10.14778/3648160.3648183](https://doi.org/10.14778/3648160.3648183)

Why it matters:

- shows that ray-tracing cores can accelerate database scan-style work beyond
  spatial join

### 2025: LibRTS

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  [*LibRTS: A Spatial Indexing Library by Ray Tracing*](https://dl.acm.org/doi/10.1145/3710848.3710850),
  Proceedings of the 30th ACM SIGPLAN Annual Symposium on Principles and
  Practice of Parallel Programming (PPoPP 2025),
  DOI: [10.1145/3710848.3710850](https://dl.acm.org/doi/10.1145/3710848.3710850)

Why it matters:

- suggests a reusable indexing/runtime substrate for future RTDL backend work

### 2025: Graph case study with ray-tracing cores

- Zhixiong Xiao, Mengbai Xiao, Yuan Yuan, Dongxiao Yu, Rubao Lee, and
  Xiaodong Zhang,
  [*A Case Study for Ray Tracing Cores: Performance Insights with
  Breadth-First Search and Triangle Counting in Graphs*](https://dl.acm.org/doi/10.1145/3727108),
  Proceedings of the ACM on Measurement and Analysis of Computing Systems,
  9(2), 2025,
  DOI: [10.1145/3727108](https://dl.acm.org/doi/10.1145/3727108)

Why it matters:

- shows that the research direction is not limited to spatial join workloads

### 2025: RayDB

- Xuri Shi, Kai Zhang, X. Sean Wang, Xiaodong Zhang, and Rubao Lee,
  [*RayDB: Building Databases with Ray Tracing Cores*](https://www.vldb.org/pvldb/vol19/p43-shi.pdf),
  Proceedings of the VLDB Endowment 19(1), 43--55, 2025,
  DOI: [10.14778/3772181.3772185](https://doi.org/10.14778/3772181.3772185)

Why it matters:

- points toward database systems built more directly around ray-tracing cores

### 2026: X-HD

- Liang Geng, Zhehu Yuan, Rubao Lee, Fusheng Wang, and Xiaodong Zhang,
  *X-HD: Fast Hausdorff Distance Computation with Ray Tracing*,
  Proceedings of the 39th ACM International Conference on Supercomputing
  (ICS 2026)

Why it matters:

- shows a geometry-heavy non-graphical workload outside the current RTDL v0.1
  release slice

## Other useful external context

Representative external background papers for RTDL's broader direction include:

- Ingo Wald et al., *Embree: A Kernel Framework for Efficient CPU Ray Tracing*,
  ACM Transactions on Graphics, 2014
- Steven G. Parker et al., *OptiX: A General Purpose Ray Tracing Engine*,
  SIGGRAPH 2010

These are not future RTDL workload papers, but they remain important because
they define the backend/runtime context RTDL builds on.

## Practical reading order

If your main interest is the current RTDL roadmap, read in this order:

1. RayJoin
2. RTScan
3. LibRTS
4. the 2025 graph case study
5. RayDB
6. X-HD

That sequence moves from the current RTDL application slice to broader
non-graphical ray-tracing systems work.
