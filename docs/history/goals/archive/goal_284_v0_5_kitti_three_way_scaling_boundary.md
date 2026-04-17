# Goal 284: v0.5 KITTI Three-Way Scaling Boundary

Purpose:
- extend the first bounded KITTI three-way result into a small scaling sweep
- verify whether the 512-point result remains correct at the next meaningful size
- capture any correctness boundary honestly instead of overclaiming smooth scaling

Success criteria:
- a checked-in scaling script exists
- the sweep runs on Linux against real KITTI data
- the result records at least:
  - `512`
  - `1024`
  point packages
- the result records both performance medians and parity status
- if parity fails, the report records the first mismatch clearly

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
