# Goal1010 Public RTX README Wording Application

Date: 2026-04-26

Status: **implemented locally**

Scope:

- Applied the Goal1009 accepted wording to the README NVIDIA RT-Core Claim Boundary section.
- Added the seven reviewed prepared RTX A5000 query/native sub-path timing statements.
- Kept `robot_collision_screening / prepared_pose_flags` excluded because it remains below the 100 ms public-review timing floor.
- Preserved the boundary that these are not whole-app, default-mode, Python-postprocess, or broad RT-core acceleration claims.

Verification:

- `tests/goal1010_public_rtx_readme_wording_test.py` checks that the README contains the accepted wording, the robot exclusion, and links to the Goal1008/Goal1009 artifact trail.

Boundary:

- This goal applies already reviewed sub-path wording only.
- It does not authorize any broader speedup claim and does not promote blocked rows.
