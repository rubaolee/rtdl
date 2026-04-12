# Goal 283: v0.5 KITTI Three-Way Performance Result

Purpose:
- produce the first honest three-way KITTI performance comparison across:
  - RTDL reference
  - cuNSearch CUDA
  - PostGIS 3D
- use the same bounded real KITTI packages for all three systems
- separate one-time setup costs from repeated execution costs where that matters

Success criteria:
- a checked-in benchmark script exists
- the benchmark runs on Linux against real KITTI data
- PostGIS uses the hardened 3D indexed path
- cuNSearch compile cost is separated from repeated run cost
- the report records the bounded settings, parity state, and measured medians clearly

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
