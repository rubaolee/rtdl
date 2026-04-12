# Goal 271 Report: v0.5 KITTI Bounded Loader

Date: 2026-04-12
Status: implemented

## Purpose

Turn the bounded KITTI frame manifest into a real point-loading path that
returns deterministic RTDL `Point3D` records.

## What Landed

### Updated module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_kitti.py`

Added:

- `KittiBoundedPointPackage`
- `load_kitti_bounded_points_from_manifest(...)`

Extended:

- `write_kitti_bounded_package_manifest(...)`

The manifest now records:

- `max_points_per_frame`
- `max_total_points`
- the bounded point truncation rule

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported:

- `KittiBoundedPointPackage`
- `load_kitti_bounded_points_from_manifest(...)`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal270_v0_5_kitti_bounded_acquisition_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal271_v0_5_kitti_bounded_loader_test.py`

The focused test slice verifies:

- bounded manifest writing includes frame and point caps
- loading returns stable `Point3D` records
- per-frame and total truncation are deterministic
- malformed KITTI `.bin` files fail honestly
- unsupported manifest kinds fail honestly

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal270_v0_5_kitti_bounded_acquisition_test tests.goal271_v0_5_kitti_bounded_loader_test tests.goal268_v0_5_bounded_dataset_manifest_test`
- `Ran 13 tests`
- `OK`

## Honesty Boundary

This goal does not claim:

- the selected package is paper-faithful already
- any cuNSearch run has happened
- any 3D nearest-neighbor parity is closed beyond the bounded point-loading path

It only turns the KITTI bounded-manifest layer into an executable RTDL input
package for later comparison work.
