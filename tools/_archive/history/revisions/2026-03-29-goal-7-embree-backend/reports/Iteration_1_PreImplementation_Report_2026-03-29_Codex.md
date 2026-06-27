# Iteration 1 Pre-Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-7-embree-backend
Repo: /Users/rl2025/rtdl_python_only
Baseline Commit: 4e2be7f1aa72a42f609e6045396bef47071441e8

## Current State

RTDL now has:

- a Python DSL frontend
- lowering/codegen for the current workload surface
- a Python CPU simulator via `rt.run_cpu(...)`

What is still missing is a real native runtime backend on this Mac.

## Proposed Goal 7 Shape

Implement an Embree-backed runtime path for the current RTDL workloads.

The likely public API is:

- `rt.run_embree(kernel_fn, **inputs)`

This should coexist with:

- `rt.run_cpu(kernel_fn, **inputs)`

so the simulator remains the reference baseline while Embree becomes the first
native runtime backend.

## Important Practical Fact

Embree is not currently detected in the local environment:

- `brew list --versions embree` returned nothing
- `pkg-config` did not find `embree4` or `embree3`

So Goal 7 must include environment bring-up, not only runtime coding.

## Main Questions For Review

1. Is `rt.run_embree(...)` the right public API?
2. Is it acceptable to keep `rt.run_cpu(...)` as the correctness oracle and
   compare Embree results against it?
3. For the current four workloads, what should count as sufficient proof that
   the Embree backend is correct?
4. What risks or design corrections matter before coding starts?
