# Goal 296: v0.5 Native 3D KNN Oracle Closure

Purpose:
- close the remaining native `run_cpu(...)` path for 3D nearest-neighbor work
- make plain `knn_rows` over `Points3D` a real native/oracle-backed capability
- complete the native/oracle 3D point nearest-neighbor surface without
  overclaiming accelerated backend closure

Success criteria:
- the native oracle ABI gains an additive 3D `knn_rows` entrypoint
- `run_cpu(...)` matches `run_cpu_python_reference(...)` for 3D `knn_rows`
- focused regression tests pass

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
