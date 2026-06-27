# Goal 261: v0.5 Native 3D Point Contract Closure

Date: 2026-04-11
Status: implemented

## Purpose

Harden native nearest-neighbor entrypoints so the newly added 3D point surface
cannot be mistaken for native closure before the real backend work exists.

## What Landed

- Embree point packing now rejects `Point3D`
- OptiX point packing now rejects `Point3D`
- prepared Embree, OptiX, and Vulkan nearest-neighbor point paths now reject
  3D point layouts explicitly before native execution
- regression tests cover the rejection behavior

## Why This Matters

Without this slice, the repo risked a misleading state where a `Point3D`
payload could enter a native point packer and silently lose `z`.

This goal closes that honesty gap.

## Verification

Covered by:

- `tests/goal261_v0_5_native_3d_point_contract_test.py`

The slice verifies that native point paths reject 3D nearest-neighbor inputs
with explicit messages instead of fake 2D fallback behavior.
