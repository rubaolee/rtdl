# Goal 285: v0.5 cuNSearch Duplicate-Point Boundary

Purpose:
- isolate the first strict cuNSearch correctness failure into a minimal reproducible case
- determine whether the `1024`-point KITTI mismatch is broad drift or a duplicate-point boundary
- save a concrete evidence trail before attempting any mitigation

Success criteria:
- a checked-in duplicate-audit helper exists
- a checked-in probe script exists
- the minimal KITTI reproducer is recorded with exact query/search ids
- the report states whether the failure still occurs in the tiny duplicate case
- the report stays honest about what is still unknown

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
