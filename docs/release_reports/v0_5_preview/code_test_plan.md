# RTDL v0.5 Code Test Plan

Date: 2026-04-12
Status: pre-release test plan

This is the intended code-test surface for the `v0.5` pre-release phase.

## Core Regression Gate

Run:

```bash
python3 -m unittest tests.claude_v0_5_full_review_test
```

Purpose:

- broad regression guard for the current `v0.5` line

## Focused Runtime / NN Gate

Run:

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

Purpose:

- explicit nearest-neighbor/runtime gate for the current `v0.5` line

## Platform Boundary Reminder

- Linux is the primary performance-validation host
- Windows/local macOS are bounded correctness hosts
- this test plan does not require Windows/macOS performance reruns

## Release-Gate Intent

The final pre-release test slice should save:

- commands used
- pass/fail result
- any bounded exclusions
