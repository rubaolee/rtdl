# Goal 275: v0.5 cuNSearch Live Driver

Date: 2026-04-12
Status: proposed

## Purpose

Turn the bounded cuNSearch request contract into a real live Linux execution
path by compiling and running a minimal driver against a built cuNSearch
library.

## Why This Goal Matters

After Goal 273, the repo could only write and parse bounded artifacts. It still
could not execute cuNSearch itself.

This goal closes that gap for bounded local runs by using Python orchestration
to compile a tiny CUDA driver against a built cuNSearch library.

## Scope

This goal will:

1. detect a built cuNSearch header/library pair
2. generate a minimal CUDA driver from the fixed-radius request JSON
3. compile that driver with `nvcc`
4. execute it and write the bounded response JSON
5. surface compile/runtime failures honestly

## Non-Goals

This goal does not:

- claim paper-fidelity reproduction
- claim KITTI execution is online
- claim every cuNSearch configuration is supported

## Done When

This goal is done when the public Python surface can:

- resolve a built cuNSearch library configuration
- execute a bounded fixed-radius request live on Linux
- emit the same response format that Goal 273 parses
