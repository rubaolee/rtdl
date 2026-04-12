# Goal 270 Report: v0.5 KITTI Bounded Acquisition Helper

Date: 2026-04-12
Status: implemented

## Purpose

Turn the first RTNN bounded manifest into a real local acquisition helper for
KITTI-derived Velodyne frame sets.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_kitti.py`

Added:

- `KittiSourceConfig`
- `KittiFrameRecord`
- `resolve_kitti_source_root(...)`
- `kitti_source_config(...)`
- `discover_kitti_velodyne_frames(...)`
- `select_kitti_bounded_frames(...)`
- `write_kitti_bounded_package_manifest(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported the KITTI helper types and functions.

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal270_v0_5_kitti_bounded_acquisition_test.py`

The test slice verifies:

- planned status when no source root is configured
- stable sorted discovery of Velodyne frame records
- deterministic bounded frame selection
- coherent JSON manifest writing
- honest failure when the source root is absent

## Honesty Boundary

This goal does not claim:

- KITTI download is solved
- the dataset is checked into the repo
- any execution path is online for the selected frames

It only makes the first bounded acquisition helper real for a local KITTI tree.
