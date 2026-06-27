# Goal 312: Linux Large-Scale Native vs Embree vs OptiX Performance

Purpose:
- establish the first honest large-scale Linux backend comparison across:
  - native CPU/oracle
  - Embree
  - OptiX
- run that comparison on real duplicate-free KITTI 3D point packages
- capture whether the first OptiX 3D nearest-neighbor line is both fast and
  parity-clean at a scale that matters

Success criteria:
- a real Linux benchmark script exists for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- the script records native medians plus prepared Embree and OptiX setup/hot
  timings separately
- the benchmark runs on `lestat-lx1` at `16384 x 16384` duplicate-free KITTI
  scale
- parity is checked against the native CPU/oracle path for both accelerated
  backends
- the report states the honest outcome workload by workload

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
