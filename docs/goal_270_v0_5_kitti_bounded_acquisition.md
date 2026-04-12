# Goal 270: v0.5 KITTI Bounded Acquisition Helper

Date: 2026-04-12
Status: proposed

## Purpose

Turn the first RTNN bounded dataset manifest into a real local acquisition
helper for the KITTI family.

## Why This Goal Matters

The repo already has:

- KITTI in the RTNN dataset registry
- a bounded KITTI manifest contract
- a cuNSearch adapter skeleton

What it still lacks is a concrete helper that can point at a local KITTI source
root, discover real Velodyne frames, and freeze a deterministic bounded subset
for later Linux comparison work.

## Scope

This goal will:

1. add a KITTI-specific source-root/config helper
2. discover Velodyne `.bin` frames from a local KITTI tree
3. select a deterministic bounded subset by stable order and stride
4. write a bounded KITTI package manifest artifact
5. add focused tests for discovery, selection, and manifest writing

## Non-Goals

This goal does not:

- download KITTI from the internet
- claim the full dataset is bundled in the repo
- run RTDL or cuNSearch on the selected frames yet

## Done When

This goal is done when the public Python surface can:

- resolve a local KITTI source root
- enumerate stable frame records
- select a bounded frame set
- write a JSON bounded package manifest for downstream Linux runs
