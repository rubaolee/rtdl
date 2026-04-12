# Goal 299: Embree 3D Bounded-KNN Closure

Purpose:
- bring the Embree backend online for the second v0.5 3D point nearest-neighbor
  workload:
  - `bounded_knn_rows`
- reuse the newly closed Embree 3D fixed-radius candidate collection path where
  that is technically coherent, instead of inventing duplicate native machinery
- keep the honesty boundary explicit:
  - Embree 3D `fixed_radius_neighbors`: online
  - Embree 3D `bounded_knn_rows`: online
  - Embree 3D `knn_rows`: still blocked for a later goal

Success criteria:
- `run_embree(...)` matches `run_cpu_python_reference(...)` for a focused 3D
  `bounded_knn_rows` case
- prepared Embree execution works on the same 3D bounded-KNN case
- raw-mode output includes `neighbor_rank`
- the report explains that the ranking layer currently reuses the native
  fixed-radius Embree rows and adds bounded ranks in Python

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
