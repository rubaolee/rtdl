# Goal 277 Report: v0.5 KITTI Linux Acquisition Prep

Date: 2026-04-12
Status: implemented

## Purpose

Prepare the Linux host for the first real KITTI-backed `v0.5` run and stop
exactly at the manual official-download boundary.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_kitti_ready.py`

Added:

- `KittiLinuxReadyReport`
- `inspect_kitti_linux_source_root(...)`
- `write_kitti_linux_ready_report(...)`

### New script

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal277_kitti_linux_ready.py`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal277_v0_5_kitti_linux_ready_test.py`

The test slice verifies:

- missing-root reporting
- empty-root reporting
- ready-root reporting when Velodyne `.bin` files exist
- JSON report writing

## Linux Staging Path

Canonical Linux staging path prepared:

- `/home/lestat/data/kitti_raw`

This directory now exists on `lestat-lx1`.

## Readiness Result

Current Linux readiness result:

- source root: `/home/lestat/data/kitti_raw`
- current_status: `empty`
- velodyne_bin_count: `0`

So the repo and Linux host are prepared, but the dataset is still absent.

## Manual Boundary

Official KITTI raw data requires manual login on the KITTI site before
download. This goal does not bypass that boundary.

## Exact Next Commands

After the dataset is placed on Linux:

```bash
ssh lestat-lx1
export RTDL_KITTI_SOURCE_ROOT=/home/lestat/data/kitti_raw
cd /home/lestat/work/rtdl_v05_live
PYTHONPATH=src:. python3 scripts/goal277_kitti_linux_ready.py \
  /home/lestat/data/kitti_raw \
  --write-json build/goal277_kitti_linux_ready_report.json
cat build/goal277_kitti_linux_ready_report.json
```

If the report shows `current_status = "ready"`, the next autonomous repo goal is
the first real KITTI bounded package run on Linux.
