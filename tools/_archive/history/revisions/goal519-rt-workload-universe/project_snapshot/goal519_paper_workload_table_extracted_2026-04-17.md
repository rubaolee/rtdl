# Goal519 Extracted Workload Table From arXiv 2603.28771v1

Source: `/Users/rl2025/Downloads/2603.28771v1.pdf`

This is a compact extracted checklist from the paper's Table 3 and Table 4,
used only as review evidence for Goal519.

## Workloads Listed

- Penetration Depth
- SpMM
- BFS
- Triangle Counting
- Set Intersection
- Binary Search
- Point Queries
- Range Queries
- Barnes-Hut
- Discrete CD
- Continuous CD
- RMQ
- Line-Segment Intersection
- Point in Polygon
- Non-euclidean kNN
- ANN
- Outlier Detection
- Index Scan
- kNN
- Particle Simulation
- Radio Wave Propagation
- DBSCAN
- Point Location
- FRNN
- Particle Tracking
- Graph Drawing
- Space Skipping
- Segmentation
- Particle-Mesh Coupling
- Infrared Radiation
- Particle Transport
- Voxelization

## Paper-Level Guidance Extracted

- Nearest-neighbor/proximity variants are among the strongest RT-core
  candidates.
- Heuristic and approximate workloads can benefit because they reduce the work
  performed during traversal.
- Latency-bound graph workloads such as BFS can be weak performance candidates
  even when expressible.
- Many short rays are generally preferable to a few long rays.
- Strong mappings represent data as geometric objects, map queries to rays, and
  interpret intersections as operations or query results.
- Major limitations include rigid RT-core programming models, lack of internal
  BVH-node access, memory blow-up for abstract index encodings, FP32 geometric
  precision, 3D coordinate limits for high-dimensional problems, divergence, and
  RT/CUDA context switching overhead.
