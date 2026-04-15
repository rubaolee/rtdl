# Codex Consensus: Goal 386 v0.6 RT Graph Kernel Surface Design

Date: 2026-04-14
Reviewer: Codex

## Consensus

I agree with the accepted Gemini and Claude reviews.

The most important correction in this design is the host/kernel split. A
paper-aligned BFS path cannot hide the full frontier loop in one synthetic
kernel. The kernel must represent the RT-based expansion step while the host
controls iteration and synchronization. The same boundary is correct for
triangle counting.

I also agree with Claude's forward note that graph kernels should not silently
inherit geometry-oriented precision wording forever. That belongs in the next
lowering/runtime-contract goal.

## Final Decision

Goal 386 closes as accepted.

The repo now has a technically coherent design plan for how RTDL users would
author RT graph kernels before any implementation claim is made.
