# Goal 78 Plan: Vulkan Positive-Hit Sparse Redesign

## Problem Statement

The current Vulkan positive-hit `pip` implementation is correctness-clean but structurally slow on long county workloads because it still performs dense host-side exact finalization after GPU execution.

## Current Waste

- GPU writes dense `point_count × poly_count` rows
- host downloads dense rows
- host exact-finalizes every pair

This makes the positive-hit mode behave like a full scan with extra GPU overhead.

## Target Redesign

- GPU emits sparse candidate pairs only
- host exact-finalizes candidate pairs only
- final emitted rows preserve exact parity with PostGIS and the oracle hierarchy

## Review Path

- Claude implementation first
- Codex review second
- Gemini review third
- publish only after at least 2 usable approvals
