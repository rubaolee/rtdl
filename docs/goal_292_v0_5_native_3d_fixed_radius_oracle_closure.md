# Goal 292: v0.5 Native 3D Fixed-Radius Oracle Closure

Purpose:
- close the first native `run_cpu(...)` path for a 3D nearest-neighbor workload
- make `fixed_radius_neighbors` over `Points3D` a real native/oracle-backed
  capability instead of a Python-reference-only path
- keep the boundary explicit for the rest of the 3D nearest-neighbor family

Success criteria:
- the native oracle ABI gains an additive 3D fixed-radius entrypoint
- `run_cpu(...)` matches `run_cpu_python_reference(...)` for 3D
  `fixed_radius_neighbors`
- other 3D nearest-neighbor native paths remain honestly blocked
- focused regression tests pass

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
