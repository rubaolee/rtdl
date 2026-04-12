# Goal 272: v0.5 KITTI Point Package

Date: 2026-04-12
Status: proposed

## Purpose

Turn the executable KITTI bounded loader into a portable bounded point-package
artifact that no longer depends on a live source-root checkout.

## Why This Goal Matters

After Goal 271, the repo can load bounded KITTI points from a saved manifest,
but that manifest still depends on the original Velodyne source files being
present.

This goal closes the next packaging gap by materializing the bounded points into
a portable package file that later comparison and adapter goals can consume
directly.

## Scope

This goal will:

1. add a writer for a portable bounded KITTI point package
2. add a loader for that package
3. preserve stable point ids and package metadata
4. add focused tests for materialization and round-trip loading

## Non-Goals

This goal does not:

- claim paper-fidelity dataset closure
- execute cuNSearch
- run any full RTNN comparison matrix

## Done When

This goal is done when the public Python surface can:

- materialize bounded KITTI points into a portable package artifact
- load that package back into deterministic RTDL `Point3D` records
- fail honestly on unsupported package kinds
