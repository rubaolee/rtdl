# Goal 291: v0.5 KITTI 16384 Boundary Continuation

Purpose:
- extend the duplicate-free KITTI scaling line to `16384` points
- determine whether the existing cuNSearch large-set correctness boundary still
  persists when the search window is widened enough to recover a duplicate-free
  pair
- capture the first point where the RTDL Python reference path becomes
  materially expensive for repeated three-way runs

Success criteria:
- the duplicate-free `16384` three-way result is recorded
- the report states whether the widened search window changes the correctness
  reading
- the report states whether `16384` introduces a new failure shape or continues
  the known large-set boundary

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
