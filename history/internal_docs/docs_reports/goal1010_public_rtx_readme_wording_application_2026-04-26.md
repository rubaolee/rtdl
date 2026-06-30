# Goal1010 Public RTX README Wording Application

Date: 2026-04-26

Status: **implemented locally; expanded to secondary public status docs**

Scope:

- Applied the Goal1009 accepted wording to the README NVIDIA RT-Core Claim Boundary section.
- Added the seven reviewed prepared RTX A5000 query/native sub-path timing statements.
- Kept `robot_collision_screening / prepared_pose_flags` excluded because it remains below the 100 ms public-review timing floor.
- Preserved the boundary that these are not whole-app, default-mode, Python-postprocess, or broad RT-core acceleration claims.
- Synchronized `docs/v1_0_rtx_app_status.md` with the seven reviewed public sub-path wording rows and the robot block.
- Synchronized `docs/app_engine_support_matrix.md` so robot remains a real RT-core path but is blocked for public speedup wording by Goal1008.

Verification:

- `tests/goal1010_public_rtx_readme_wording_test.py` checks that the README contains the accepted wording, the robot exclusion, and links to the Goal1008/Goal1009 artifact trail.
- The same test also checks that `docs/v1_0_rtx_app_status.md` and `docs/app_engine_support_matrix.md` preserve the robot public-wording block.

Boundary:

- This goal applies already reviewed sub-path wording only.
- It does not authorize any broader speedup claim and does not promote blocked rows.
