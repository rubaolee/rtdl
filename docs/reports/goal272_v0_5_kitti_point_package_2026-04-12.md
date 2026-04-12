# Goal 272 Report: v0.5 KITTI Point Package

Date: 2026-04-12
Status: implemented

## Purpose

Turn the executable bounded KITTI manifest into a portable bounded point-package
artifact for later Linux comparison work.

## What Landed

### Updated module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_kitti.py`

Added:

- `write_kitti_bounded_point_package(...)`
- `load_kitti_bounded_point_package(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported:

- `write_kitti_bounded_point_package(...)`
- `load_kitti_bounded_point_package(...)`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal272_v0_5_kitti_point_package_test.py`

The focused test slice verifies:

- portable package materialization from a bounded KITTI manifest
- stable point-id preservation in the written package
- round-trip loading into RTDL `Point3D` records
- honest failure on unsupported package kinds

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal270_v0_5_kitti_bounded_acquisition_test tests.goal271_v0_5_kitti_bounded_loader_test tests.goal272_v0_5_kitti_point_package_test`
- `Ran 12 tests`
- `OK`

## Honesty Boundary

This goal does not claim:

- the package is paper-faithful
- the package is the final reproduction artifact
- any external baseline execution is online

It only makes the bounded KITTI points portable so the next execution goals can
consume a stable on-disk input package.
