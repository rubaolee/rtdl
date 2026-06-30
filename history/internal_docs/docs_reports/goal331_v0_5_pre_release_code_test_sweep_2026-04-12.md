# Goal 331 Report: v0.5 Pre-Release Code-Test Sweep

Date:
- `2026-04-12`

Goal:
- run the explicit `v0.5` pre-release code-test gate defined in
  `docs/release_reports/v0_5_preview/code_test_plan.md`

Commands run:

```bash
python3 -m unittest tests.claude_v0_5_full_review_test
```

```bash
python3 -m unittest \
  tests.goal292_v0_5_native_3d_fixed_radius_oracle_test \
  tests.goal293_v0_5_native_3d_bounded_knn_oracle_test \
  tests.goal296_v0_5_native_3d_knn_oracle_test \
  tests.goal298_v0_5_embree_3d_fixed_radius_test \
  tests.goal299_v0_5_embree_3d_bounded_knn_test \
  tests.goal300_v0_5_embree_3d_knn_test \
  tests.goal315_v0_5_vulkan_3d_nn_test \
  tests.goal328_v0_5_layout_types_name_collision_test
```

Results:
- core regression gate:
  - `Ran 112 tests`
  - `OK`
- focused runtime / NN gate:
  - `Ran 21 tests`
  - `OK (skipped=4)`

Focused-gate note:
- the `skipped=4` result is expected in this bounded sweep
- those skips come from backend/platform-conditioned tests inside the focused
  suite rather than a failure of the pre-release gate

Honesty boundary:
- this is a pre-release code-test slice, not the final release audit
- Linux remains the primary performance-validation host
- Windows/local macOS are still bounded correctness hosts and are not part of
  this code-test performance gate
