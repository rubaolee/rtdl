# Goal 289: v0.5 KITTI 4096 Boundary

Purpose:
- capture the first large duplicate-free KITTI size where cuNSearch strict parity breaks again
- determine whether the `4096` failure is still a duplicate-point issue or a broader large-set boundary
- preserve an honest evidence trail before any further scale-up

Success criteria:
- the duplicate-free `4096` result is recorded clearly
- the mismatch count and first differing row are saved
- a checked-in probe script tests the first failing query against a reduced candidate subset
- the report states whether the reduced subset reproduces the failure

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
