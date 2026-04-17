# Goal 276: v0.5 Live Bounded Linux Comparison

Date: 2026-04-12
Status: proposed

## Purpose

Close the first live bounded Linux comparison loop by running cuNSearch on the
same portable 3D packages that RTDL uses and reporting parity honestly.

## Why This Goal Matters

After Goals 274 and 275, the repo had:

- an offline comparison harness
- a live bounded cuNSearch execution path

What it still lacked was a single live comparison result that connected them.

## Scope

This goal will:

1. add a helper that writes the request, runs the live driver, and compares the result
2. reuse portable bounded KITTI-style point packages
3. report row counts and parity honestly
4. validate the flow on Linux with a bounded synthetic 3D package

## Non-Goals

This goal does not:

- claim KITTI execution is online
- claim paper-fidelity reproduction
- claim all future live comparisons will be this easy

## Done When

This goal is done when the repo has one real live bounded Linux comparison
result for `fixed_radius_neighbors` on portable 3D packages.
