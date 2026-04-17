# Goal 288: v0.5 KITTI Duplicate-Free Three-Way

Purpose:
- rerun the bounded three-way KITTI comparison on duplicate-free frame pairs
- verify that the cuNSearch line remains correct once the known duplicate-point boundary is removed
- extend the live comparison line past the blocked `1024` duplicate case

Success criteria:
- a checked-in duplicate-free three-way benchmark script exists
- the benchmark runs on Linux against real KITTI data
- the selected frame pairs are recorded
- parity holds for:
  - PostGIS
  - cuNSearch
  on the duplicate-free packages
- the report records bounded medians honestly

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
