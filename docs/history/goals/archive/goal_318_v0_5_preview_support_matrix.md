# Goal 318: v0.5 Preview Support Matrix

Purpose:
- convert the current `v0.5` backend/platform state into a release-facing
  preview support matrix
- make the current Linux 3D nearest-neighbor closure explicit without
  overclaiming Windows or macOS maturity
- give the `v0.5` line a single current-state support artifact instead of
  leaving the backend picture scattered across reports

Success criteria:
- create a `docs/release_reports/v0_5_preview/support_matrix.md` file
- describe current backend roles across:
  - Python reference
  - native CPU / oracle
  - PostGIS
  - Embree
  - OptiX
  - Vulkan
- describe current platform roles across:
  - Linux
  - local macOS
  - Windows
- keep the Linux large-scale ordering explicit
- keep the Windows/macOS and PostGIS honesty boundaries explicit
- record bounded Windows/macOS Embree correctness explicitly rather than
  leaving those platforms as vague portability placeholders

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
