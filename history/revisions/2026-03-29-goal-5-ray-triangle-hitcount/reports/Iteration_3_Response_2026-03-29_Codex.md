# Iteration 3 Response

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-5-ray-triangle-hitcount

## Outcome

The first Gemini-authored Goal 5 program was invalid RTDL.

Gemini produced an imagined imperative kernel model with:

- typed function arguments,
- a loop over triangles,
- a non-existent `rt.intersect(...)`,
- a non-existent `rt.Output[...]`,
- a non-existent `rt.KernelRole.RAY`.

## Interpretation

This is a documentation sufficiency failure, not a compiler failure.

The current docs still left enough room for Gemini to regress into a more
general-purpose kernel language instead of the current constrained RTDL kernel
shape.

## Revision Plan

Codex will revise the RTDL docs to make the following rules explicit:

- RTDL kernels take no Python function arguments.
- RTDL is declarative, not imperative.
- RTDL does not support loops, local accumulation, or user-written intersection calls.
- All kernels must use the exact `input -> traverse -> refine -> emit` structure.
- Unsupported constructs should be called out explicitly for LLMs.

After that, Gemini will be asked to author the Goal 5 program again.
