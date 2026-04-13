# Goal 321 Report: v0.5 Frontpage Clarity

Date:
- `2026-04-12`

Goal:
- make the README front page understandable to a reader who does not already
  know the backend names or current support boundary

File changed:
- `README.md`

What changed:
- added a `Version Status At A Glance` section
- added a `Backend Names In Plain English` section
- added an `OS Support At A Glance` section
- made the front page explicitly distinguish:
  - released `v0.4.0`
  - active `v0.5 preview`
- linked the front page to:
  - `docs/release_reports/v0_5_preview/support_matrix.md`

Most important clarity improvements:
- `CPU/oracle` is now explained as RTDL's compiled C/C++ correctness baseline
- `OptiX` is now explained as the NVIDIA GPU ray-tracing backend
- `Vulkan` is now explained as the Vulkan ray-tracing GPU backend
- Windows and local macOS are now described as bounded correctness platforms,
  not implied performance peers to Linux

Honesty boundary preserved:
- Linux remains the only large-scale nearest-neighbor performance claim surface
- Windows and local macOS stay bounded
- the README now points readers to the preview support matrix instead of making
  them infer support status from partial wording
