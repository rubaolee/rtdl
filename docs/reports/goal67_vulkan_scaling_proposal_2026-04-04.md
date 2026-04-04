# Goal 67 Vulkan Scaling Proposal

Date: `2026-04-04`

## Proposal

Attempt a safe Vulkan `lsi` scaling patch by:

- tiling the Vulkan `lsi` GPU traversal stage across right-side chunks
- preserving the current accepted correctness contract
- keeping final exact truth on the host side

Additional live-doc work in the same round:

- update canonical docs to reflect that:
  - v0.1 is reached under the accepted bounded rule
  - Vulkan is parity-clean on the accepted bounded Linux surface
  - Vulkan is still provisional for larger-scale use

## Intended Benefit

The intended benefit of the code patch was:

- remove immediate capacity failures on larger `lsi` packages
- avoid claiming broader correctness than Goal 66 already established

## Important Limitation

This proposal was exploratory.

It was not accepted before external review.
