# Goal 287: v0.5 KITTI Duplicate-Free Selector

Purpose:
- find bounded KITTI frame pairs that do not contain exact cross-package duplicate points
- turn the duplicate-point guard from a hard stop into a practical selection workflow
- preserve strict cuNSearch parity comparisons on valid bounded inputs

Success criteria:
- a checked-in selector exists
- the selector scans a bounded search window and returns the first duplicate-free pair
- focused tests show it skips a duplicate pair and finds the next clean pair
- the result is ready to feed into a duplicate-free three-way benchmark goal

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
