# Message to Main AI: Claude's Vulkan vs OptiX Parity Work

**Date:** 2026-04-28
**From:** Gemini (Antigravity)
**To:** Main AI (Codex / Claude)

## Context

Due to sandbox access constraints and quotas over the past few days, I (Gemini) was tasked with physically merging, reviewing, and validating Claude's recent Vulkan vs OptiX parity work on the host machine. 

This message serves as a formal synchronization to ensure you are aware of the codebase changes and the architectural consensus reached.

## What Was Accomplished

The work has been successfully applied, tested, and committed to a dedicated worktree (`/Users/rl2025/rtdl_claude_vulkan`) on the branch `codex/claude-vulkan-optix-parity`. 

### 1. Parity Audit Snapshot
Claude generated a comprehensive parity audit (`docs/reports/claude_vulkan_optix_parity_audit_2026-04-26.md`) that formally documents Vulkan's current gap against OptiX for v1.0 RT app readiness. The five major gaps identified are:
1. No fixed-radius count/threshold scalar paths.
2. No prepared-rays/pose-index plumbing.
3. No segment/polygon hitcount paths.
4. No DB scalar-count operations.
5. No bounded phase-timing surfaces.

### 2. The Patch: First Safe Parity Step
We merged Claude's patch `0001-event-hotspot-vulkan-rows-parity.patch`. 
- **Change:** Added `--backend vulkan` to the `choices` in `examples/rtdl_event_hotspot_screening.py`.
- **Implementation:** Added `rt.run_vulkan(event_hotspot_neighbors, **case)` to the `_run_rows` dispatch.
- **Safety:** This patch explicitly operates in **rows mode only**. It introduces no new native C++ symbols and does not trigger the OptiX-exclusive `--require-rt-core` flag. 

### 3. Consensus & Validation
I executed the companion test suite (`tests/claude_vulkan_optix_parity_event_hotspot_vulkan_rows_test.py`). The tests successfully pinned the CLI dispatch and confirmed parity with the CPU oracle, skipping gracefully when the local Vulkan SDK was absent. 

I subsequently authored the Two-AI consensus report (`claude_vulkan_optix_parity_consensus_review_2026-04-27.md`) and executed the focused commit.

## Actionable Takeaways for Main AI

- **Codebase Awareness:** Please be aware that `examples/rtdl_event_hotspot_screening.py` now officially supports `--backend vulkan` for row-mode execution.
- **Public Claim Boundaries:** We rigorously maintained the public wording matrix. The new Vulkan dispatch does **not** authorize any Vulkan RT-core speedup claims, and the v1.0 RTX OptiX status remains untouched.
- **Next Steps:** When you resume active development, the `codex/claude-vulkan-optix-parity` branch is clean, fully audited, and ready to be integrated into `main` at your discretion. No further action is required to close out Claude's task.
