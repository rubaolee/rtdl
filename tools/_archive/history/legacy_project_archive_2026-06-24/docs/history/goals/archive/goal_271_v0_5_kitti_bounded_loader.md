# Goal 271: v0.5 KITTI Bounded Loader

Date: 2026-04-12
Status: proposed

## Purpose

Turn the bounded KITTI frame manifest into a real point-loading path that
produces deterministic RTDL `Point3D` records.

## Why This Goal Matters

After Goal 270, the repo can freeze a bounded KITTI frame list, but it still
cannot execute that list into RTDL-ready 3D points. That means the dataset
layer is still metadata-only.

This goal closes the first execution gap by making the saved manifest readable
as a bounded point package.

## Scope

This goal will:

1. define a bounded KITTI point-package result type
2. add a loader that reads KITTI Velodyne `.bin` frames from a saved manifest
3. apply deterministic per-frame and total point caps
4. return RTDL `Point3D` records with stable ids
5. add focused tests for valid loads, truncation, and invalid frame files

## Non-Goals

This goal does not:

- claim the package is paper-faithful yet
- add online third-party baseline execution
- close 3D CPU/oracle nearest-neighbor parity

## Done When

This goal is done when the public Python surface can:

- read a bounded KITTI package manifest
- load bounded 3D points from the selected frame files
- preserve a deterministic truncation rule
- fail honestly on malformed frame data
