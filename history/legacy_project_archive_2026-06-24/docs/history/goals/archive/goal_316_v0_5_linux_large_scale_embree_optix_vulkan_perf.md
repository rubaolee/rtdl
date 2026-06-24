# Goal 316: Linux Large-Scale Embree vs OptiX vs Vulkan Performance

Purpose:
- extend the current Linux large-scale 3D nearest-neighbor backend table to
  include Vulkan
- measure Embree, OptiX, and Vulkan on the same duplicate-free real KITTI
  package pair at `32768 x 32768`
- keep correctness explicit by requiring row parity across the accelerated
  backends before accepting the performance table

Success criteria:
- Vulkan is benchmarked on the same saved `32768` KITTI package pair already
  used for the expanded-data Linux backend line
- the report records hot-median timings for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- the report separates setup costs from hot timings
- Embree, OptiX, and Vulkan row parity is clean on that saved package pair
- the report keeps the role boundaries explicit:
  - PostGIS remains an external correctness/timing anchor from the already
    closed line
  - this slice focuses on the accelerated backend race

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
