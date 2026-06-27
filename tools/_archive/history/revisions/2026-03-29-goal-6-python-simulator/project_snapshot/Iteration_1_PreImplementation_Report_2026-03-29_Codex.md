# Iteration 1 Pre-Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-6-python-simulator
Repo: /Users/rl2025/rtdl_python_only
Baseline Commit: 3569438d984d695795eb9c1903f728b03a065dd1

## Current State

RTDL already has:

- a Python DSL frontend
- workload lowering and backend plan generation
- CPU reference semantics in `src/rtdsl/reference.py`
- example kernels for all currently supported workloads

What is missing is a runtime-like execution path that lets a user run an RTDL
kernel directly and receive result rows on this machine.

## Proposed Implementation Boundary

Implement a Python simulator for current RTDL kernels only.

The simulator should:

- accept a kernel function plus Python input records
- compile the kernel
- validate required input names and compatible record shapes
- convert input records into RTDL reference dataclasses
- dispatch to the existing CPU reference implementation for the workload
- return concrete result rows

## Main Questions For Review

1. Is `rt.run_cpu(kernel_fn, **inputs)` the right public interface?
2. Should inputs accept both RTDL reference dataclasses and plain dictionaries?
3. What evidence should count as completion for this goal?
4. How should the implementation be reviewed for correctness?
