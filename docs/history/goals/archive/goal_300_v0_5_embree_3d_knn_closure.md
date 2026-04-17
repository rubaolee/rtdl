# Goal 300: Embree 3D KNN Closure

Purpose:
- close the remaining Embree 3D point nearest-neighbor workload:
  - `knn_rows`
- complete the Embree 3D nearest-neighbor capability line after Goals 298 and
  299
- preserve honesty around what this does and does not close:
  - capability and focused parity closure
  - not yet cross-platform performance closure

Success criteria:
- the Embree native ABI exports a dedicated 3D `knn_rows` entrypoint
- `run_embree(...)` matches `run_cpu_python_reference(...)` on a focused 3D
  KNN case
- prepared Embree execution works on the same 3D KNN case
- tie ordering remains deterministic by `neighbor_id`
- the report keeps the platform boundary explicit

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
