# Goal 277: v0.5 KITTI Linux Acquisition Prep

Date: 2026-04-12
Status: proposed

## Purpose

Prepare the Linux host for the first real KITTI-backed `v0.5` run, stopping
exactly at the manual login/download boundary if the official dataset cannot be
scripted.

## Why This Goal Matters

After Goal 276, the repo has:

- bounded KITTI manifest and package logic
- live cuNSearch execution on Linux
- live bounded RTDL-vs-cuNSearch parity on synthetic 3D packages

What it still lacks is the real KITTI source tree on Linux.

## Scope

This goal will:

1. choose and create the canonical Linux KITTI staging path
2. add a readiness inspector for the Linux KITTI source root
3. record the exact manual download/login boundary
4. save the exact verification commands needed after the data is placed

## Non-Goals

This goal does not:

- bypass KITTI login or terms
- claim KITTI is already present
- claim real KITTI comparison has happened

## Done When

This goal is done when:

- the Linux staging path is fixed
- the repo has a readiness script and report format
- the exact manual action is documented
- the next autonomous step is clear once the dataset appears
