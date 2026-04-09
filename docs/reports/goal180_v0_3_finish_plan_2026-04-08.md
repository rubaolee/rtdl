# Goal 180 Report: v0.3 Finish Plan

Date: 2026-04-08

## Objective

Turn the current post-Goal-179 state into a bounded finish sequence for `v0.3`, so the remaining work can be executed one goal at a time under the repo's `2+` AI consensus rule.

## Current State

- `v0.2.0` is already released
- `v0.3` already includes:
  - visual-demo charter
  - Linux 3D backend parity closure
  - Windows Embree flagship-style movie work
  - Linux OptiX/Vulkan supporting artifacts
  - temporal blend option
  - 4K artifact acceptance
  - front-surface YouTube refresh
  - Linux GPU regression coverage
- the new smooth-camera line now exists as the strongest candidate for the final flagship movie because it avoids the worst moving-light blinking problem

## Remaining Finish Work

The remaining work is not "prove RTDL can do graphics" again. That is already demonstrated. The remaining work is:

1. choose and accept the final smooth-camera flagship artifact
2. package the Linux smooth-camera OptiX/Vulkan previews as supporting artifacts
3. refresh the repo front surface if the flagship artifact changes
4. write the final `v0.3` status package with clear honesty boundaries

## Proposed Ordered Goals

### Goal 181

Smooth-camera flagship acceptance:

- accept one Windows Embree smooth-camera movie
- record run facts and artifact paths
- keep known visual limitations explicit

### Goal 182

Linux smooth-camera supporting package:

- package the OptiX and Vulkan previews
- require compare-clean frame `0`
- keep them secondary to the Windows artifact

### Goal 183

Front-surface refresh:

- point the repo to the chosen flagship artifact
- keep one clear primary public-facing recommendation

### Goal 184

`v0.3` final package:

- summarize the bounded accomplishment of the line
- preserve backend/platform honesty
- state what is future work rather than pretending it is already part of the finished line

## Why This Plan Is Bounded

- it does not reopen already-closed backend correctness goals
- it does not invent a new scene family
- it keeps focus on the strongest current direction:
  - smooth camera motion
  - fixed-light rig
  - Windows Embree flagship
  - Linux GPU supporting evidence

## Review Requirement

This plan itself must receive:

- at least one external AI review
- Codex consensus

before the execution of the finish sequence is treated as formally approved.
