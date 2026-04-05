# Codex Review: Goal 78 Final Package

**Date:** 2026-04-04  
**Verdict:** APPROVE-WITH-NOTES

## Findings

- The Goal 78 report is honest about scope. It does not claim a Vulkan performance win
  and it does not hide the missing hardware-smoke-test gap.
- The local code in `src/native/rtdl_vulkan.cpp` matches the report's architectural
  claim: the old pure-CPU positive-hit full scan is gone and the new path uses sparse
  GPU candidate generation plus host exact finalization.
- The focused Python-side Vulkan tests in `tests/rtdsl_vulkan_test.py` correctly cover:
  positive-hit parity, positive-only row shape, no-false-positives, and full-matrix
  non-regression.
- Final review surfaced one real implementation issue in the sub-copy path:
  the temporary `d_sub` buffer was initially missing transfer usage flags even though it
  is used as both a `vkCmdCopyBuffer(...)` destination and a source for
  `download_from_buf(...)`. That is now fixed.

## Agreement and Disagreement

- I agree with accepting Goal 78 as an implementation closure.
- I do not agree with any stronger claim than that. Without a Vulkan-capable hardware
  run, this should not be described as a verified runtime or performance result.

## Recommended Next Step

- Treat Goal 78 as the accepted design/code closure for Vulkan positive-hit sparse
  generation.
- If Vulkan is resumed later, the next goal should be a hardware-backed smoke-test and
  measurement package, not another redesign-only round.
