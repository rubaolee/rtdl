# Goal 278 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Summary

Goal 278 corrected the KITTI acquisition layer to match the real KITTI raw-data layout and added bounded frame offsets for real query/search package splits.

## What Changed

- `src/rtdsl/rtnn_kitti.py`
  - real KITTI frame discovery now accepts both:
    - `.../velodyne/*.bin`
    - `.../velodyne_points/data/*.bin`
  - `select_kitti_bounded_frames(...)` now accepts `start_index`
  - `write_kitti_bounded_package_manifest(...)` now persists `start_index`
- `src/rtdsl/rtnn_kitti_ready.py`
  - readiness detection now recognizes real KITTI `velodyne_points`
- tests updated:
  - `tests/goal270_v0_5_kitti_bounded_acquisition_test.py`
  - `tests/goal277_v0_5_kitti_linux_ready_test.py`

## Verification

Local:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal270_v0_5_kitti_bounded_acquisition_test \
  tests.goal271_v0_5_kitti_bounded_loader_test \
  tests.goal272_v0_5_kitti_point_package_test \
  tests.goal277_v0_5_kitti_linux_ready_test

Ran 19 tests
OK
```

Linux:

```text
PYTHONPATH=src:. python3 scripts/goal277_kitti_linux_ready.py \
  /home/lestat/data/kitti_raw \
  --write-json build/goal277_kitti_linux_ready_report.json
```

Observed report:

- `current_status = "ready"`
- `velodyne_bin_count = 108`
- sample files under:
  - `2011_09_26/2011_09_26_drive_0001_sync/velodyne_points/data/*.bin`

## Result

Goal 278 is complete. The KITTI bounded acquisition layer now matches the real raw-dataset layout and supports supported consecutive-frame package splits.
