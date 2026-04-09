# Goal 68 Vulkan Problem Statement

Date: `2026-04-04`

## What The Problem Is

The current Vulkan backend is correct on the accepted bounded Linux validation
surface, but it is still not mature for larger `lsi` packages.

The two main issues are:

1. **Output-capacity design**

The current Vulkan `lsi` path sizes its GPU output buffer as though it may need
to hold the full Cartesian product of left and right segments.

That is a safe upper bound for bounded validation, but it does not scale well.
For larger packages, the allocation either:

- exceeds the current `uint32` row-count contract, or
- exceeds the current `512 MiB` guardrail

2. **Host-side exact finalization**

The current accepted Vulkan design gets final truth from exact host-side
computation.

That was the right short-term choice for correctness closure, but it means
Vulkan still pays:

- GPU traversal cost
- plus heavy CPU-side exact work

So larger-package performance and maturity remain weak even when correctness is
acceptable.

## What The Problem Is Not

The current Vulkan problem is **not**:

- a bounded-surface correctness crisis
- a documentation problem
- a missing Vulkan bring-up

Those parts are already closed.

## Why Goal 67 Was Rejected

The rejected Goal 67 scaling proposal tiled the GPU traversal stage, but it did
not solve the real maturity problem.

It still:

- discarded the GPU `lsi` results
- fell back to full host-side exact `O(N*M)` `lsi`

So it reduced one immediate allocation failure mode without creating a credible
larger-scale Vulkan path.

## What A Real Fix Must Do

A credible next Vulkan scaling fix should do at least one of these:

1. reduce the output contract so the GPU stage only records bounded candidate
   information that is actually used later
2. make the host-side exact stage consume GPU-produced candidates rather than
   recomputing the full Cartesian space
3. redesign large-package processing so Vulkan work is chunked meaningfully and
   the chunk outputs are semantically real, not dead work

## Current Recommendation

Do not patch Vulkan again until the next design is reviewed first.

The next step should be a reviewed design memo comparing:

- candidate-only GPU output
- chunked candidate/refine flow
- two-pass count-then-materialize designs

and then choosing one implementation direction explicitly.
