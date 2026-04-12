# Goal 298: Embree 3D Fixed-Radius Closure

Purpose:
- bring the Embree backend online for the first v0.5 3D point nearest-neighbor
  workload
- close 3D `fixed_radius_neighbors` on Embree without overclaiming the rest of
  the 3D nearest-neighbor line
- preserve an explicit honesty boundary:
  - Embree 3D `fixed_radius_neighbors` is online
  - Embree 3D `bounded_knn_rows` and `knn_rows` remain blocked for later goals

Success criteria:
- the Embree C ABI exports a dedicated 3D fixed-radius entrypoint
- the Python Embree runtime can pack `Points3D` inputs for this path
- `run_embree(...)` matches `run_cpu_python_reference(...)` on a focused 3D
  fixed-radius case
- prepared Embree execution also works on the same 3D fixed-radius case
- the report states the honest current platform boundary instead of pretending
  Linux and Windows were closed in this slice

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
