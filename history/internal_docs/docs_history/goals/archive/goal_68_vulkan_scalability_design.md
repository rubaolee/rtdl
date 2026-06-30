# Goal 68: Vulkan Scalability Design

## Goal

Design the next serious Vulkan maturity step after Goal 66 and the rejected
Goal 67 scaling proposal.

This goal is for:

- problem definition
- candidate design options
- review
- consensus on the next implementation direction

This goal is **not** a code patch yet.

## Why a New Goal Is Needed

Goal 66 fixed Vulkan correctness on the accepted bounded Linux surface.

But the next maturity problem remains open:

- larger-package `lsi` still runs into output-capacity limits
- Vulkan still relies heavily on host-side exact finalization
- the rejected Goal 67 patch did not solve the real large-package problem

## Required Standard

The next Vulkan fix must:

- solve a real large-package bottleneck
- avoid dead GPU work
- avoid fake scaling claims
- keep correctness boundaries explicit
- be reviewed before implementation
