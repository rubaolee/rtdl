# Codex Consensus: Goal510 Goal509 Public Documentation Follow-Through

Date: 2026-04-17

Verdict: ACCEPT

Reviewed artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal510_goal509_public_doc_followthrough_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal510_claude_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal510_gemini_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/tests/goal510_app_perf_doc_refresh_test.py`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

Consensus:

- The public docs now link Goal509 and explain the robot/Barnes-Hut Linux
  performance evidence alongside the earlier Hausdorff evidence.
- Robot collision screening is consistently described as accepted for
  CPU/Embree/OptiX and not supported on Vulkan until the per-edge hit-count
  mismatch is fixed.
- Barnes-Hut is consistently described as candidate-row generation plus
  Python-owned opening-rule and force-reduction logic, not as faithful full
  N-body solver acceleration.
- The docs preserve the v0.8 boundary: app-building over the released v0.7.0
  surface, not a new released language/backend line.

No blockers remain for Goal510.
