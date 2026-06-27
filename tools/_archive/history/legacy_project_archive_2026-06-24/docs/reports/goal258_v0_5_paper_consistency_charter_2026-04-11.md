# Goal 258: v0.5 Paper-Consistency Charter

Date: 2026-04-11
Status: implemented

## Purpose

Open the `v0.5` line with a bounded, explicit charter.

This charter says `v0.5` is primarily about:

- paper/implementation consistency
- especially the RTNN nearest-neighbor line

It is not primarily about generic feature growth or visual-demo expansion.

## Basis

This charter is grounded in the saved current-workspace RTNN gap summary:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_5_rtnn_gap_summary_2026-04-11.md`

That summary establishes the major structural gaps between current `v0.4.0`
and a paper-faithful RTNN reproduction story:

- 2D nearest-neighbor public surface vs paper's 3D evaluation story
- current `knn_rows` contract mismatch
- missing paper baseline-library harnesses
- missing paper dataset package
- missing paper ablation harnesses

## Charter Summary

`v0.5` is chartered to deliver:

1. 3D nearest-neighbor public support
2. paper-consistent KNN contract where needed
3. dataset packaging / acquisition flows
4. baseline-library comparison harnesses
5. experiment scripts and reports labeled as:
   - exact reproduction
   - bounded reproduction
   - RTDL extension

## Non-Goals

This charter explicitly excludes:

- further front-page polish as a milestone driver
- visual-demo-first growth detached from paper consistency
- renderer claims

## Why This Is The Right Next Step

Current `v0.4.0` is already documented as:

- clean
- correct
- consistent
- ready for `v0.5`

So the right next step is not more `v0.4` polishing. It is opening `v0.5`
under a discipline that keeps future claims honest.
