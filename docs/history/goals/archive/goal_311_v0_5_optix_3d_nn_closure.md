# Goal 311: OptiX 3D Nearest-Neighbor Closure

Purpose:
- close the first honest Linux OptiX bring-up for the `v0.5` 3D point
  nearest-neighbor line
- make OptiX support the same 3D point workload trio already closed on the
  CPU/oracle and Embree paths:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- prove row parity on a real Linux GPU host before any large-scale OptiX
  performance claim is made

Success criteria:
- the native OptiX ABI exports 3D point entrypoints for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- the Python OptiX runtime accepts 3D point payloads in both direct and prepared
  execution paths
- `bounded_knn_rows` is supported honestly through the same fixed-radius rows
  plus Python-side ranking strategy already used on the Embree path
- Linux `lestat-lx1` builds the OptiX shared library successfully
- focused Goal 311 tests pass on Linux against the real GPU backend with parity
  to the Python reference path

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
