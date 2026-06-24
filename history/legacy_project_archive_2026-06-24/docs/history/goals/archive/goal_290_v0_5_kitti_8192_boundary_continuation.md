# Goal 290: v0.5 KITTI 8192 Boundary Continuation

Purpose:
- extend the duplicate-free KITTI scaling line to `8192` points
- determine whether the `4096` cuNSearch correctness boundary persists at the
  next larger bounded size
- preserve an honest continuation record before considering deeper cuNSearch
  diagnosis or the next dataset family

Success criteria:
- the duplicate-free `8192` three-way result is recorded
- the report states whether PostGIS and cuNSearch parity hold
- the report states whether `8192` introduces a new failure shape or simply
  continues the known large-set boundary

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
