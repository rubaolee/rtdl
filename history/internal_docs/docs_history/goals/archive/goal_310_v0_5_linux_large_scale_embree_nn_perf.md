# Goal 310: Linux Large-Scale Embree NN Performance

Purpose:
- close the first honest Linux large-scale Embree performance slice for the
  v0.5 3D nearest-neighbor line
- measure Embree against the native CPU/oracle baseline on real duplicate-free
  KITTI point packages at a scale large enough to matter
- fix the first real Embree performance defect exposed by that run instead of
  reporting a misleading backend result

Success criteria:
- a real Linux benchmark script exists for duplicate-free KITTI 3D point
  packages across:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- the benchmark records native CPU/oracle medians and prepared Embree setup/hot
  timings separately
- the benchmark runs on `lestat-lx1` at a large scale and preserves parity
- the first large-scale Embree KNN performance defect is fixed in the backend
- the report states the honest result:
  - Embree is faster than native CPU/oracle for large-scale fixed-radius and
    bounded-KNN on Linux
  - Embree KNN improved materially but is still slower than native CPU/oracle
    at the measured `16384`-point KITTI scale

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
