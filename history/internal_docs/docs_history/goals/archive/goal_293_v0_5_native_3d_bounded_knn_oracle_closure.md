# Goal 293: v0.5 Native 3D Bounded-KNN Oracle Closure

Purpose:
- close the second native `run_cpu(...)` path for 3D nearest-neighbor work
- make `bounded_knn_rows` over `Points3D` a real native/oracle-backed
  capability
- keep the remaining 3D nearest-neighbor boundary explicit

Success criteria:
- the native oracle ABI gains an additive 3D `bounded_knn_rows` entrypoint
- `run_cpu(...)` matches `run_cpu_python_reference(...)` for 3D
  `bounded_knn_rows`
- 3D `knn_rows` remains honestly blocked
- focused regression tests pass

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
