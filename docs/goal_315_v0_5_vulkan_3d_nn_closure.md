# Goal 315: Vulkan 3D Nearest-Neighbor Closure

Purpose:
- close the first honest Vulkan bring-up for the `v0.5` 3D point
  nearest-neighbor line
- make Vulkan support the same 3D point workload trio already closed on the
  CPU/oracle, Embree, and OptiX paths:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- prove row parity on a real Linux Vulkan host before any Vulkan large-scale
  performance claim is made

Success criteria:
- the native Vulkan ABI exports 3D point entrypoints for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- the Python Vulkan runtime accepts 3D point payloads in direct and prepared
  execution paths
- `bounded_knn_rows` is supported honestly through fixed-radius rows plus
  Python-side ranking, matching the Embree and OptiX strategy
- Linux `lestat-lx1` builds the Vulkan shared library successfully in an
  isolated probe tree
- focused Goal 315 tests pass on Linux against the real Vulkan backend with
  parity to the Python reference path

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
