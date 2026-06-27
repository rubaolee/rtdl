# Codex Consensus: Goal 385 v0.6 RT Graph Version Plan

Date: 2026-04-14
Reviewer: Codex

## Consensus

I agree with the accepted Gemini review.

The important correction is not "add graph support," but "restore the RTDL
identity." The graph line must be authored through RTDL kernels and interpreted
through the paper-style RT approach before any backend-expansion claims become
meaningful.

Goal 385 therefore closes as an accepted direction-setting goal.

## Required Follow-On

Goal 386 must define the graph kernel surface in a way that:

- preserves the current RTDL authoring model where possible
- states any graph-specific extension explicitly
- does not pretend the geometry-only DSL already supports graph kernels

No backend closure should be called active until that surface exists.
