# Goal1011 Claude Review

Date: 2026-04-26

Verdict: ACCEPT

Claude reviewed:

- `src/rtdsl/app_support_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal1011_rtx_public_wording_matrix_test.py`
- `tests/goal1010_public_rtx_readme_wording_test.py`
- `docs/v1_0_rtx_app_status.md`
- `docs/app_engine_support_matrix.md`
- `docs/reports/goal1011_rtx_public_wording_matrix_2026-04-26.md`

Review conclusion:

- The new `rtx_public_wording_matrix()` layer is the correct abstraction.
- `robot_collision_screening` correctly remains `ready_for_rtx_claim_review` and `rt_core_ready` because it has a real prepared OptiX ray/triangle any-hit traversal path.
- The same app is correctly `public_wording_blocked` because Goal1008 larger repeats stayed below the 100 ms public-review timing floor.
- All 18 apps are covered by the public wording matrix: 7 reviewed, 1 blocked, 8 not reviewed, and 2 non-NVIDIA targets.
- The new tests directly protect the robot three-way split.

Claude noted one non-blocking stale string: the robot maturity `cloud_policy`
in source still said to include robot in the next batched cloud run while the
newer docs said no new pod is needed unless redesign/reprofiling is planned.
Codex fixed that source string after the review.
