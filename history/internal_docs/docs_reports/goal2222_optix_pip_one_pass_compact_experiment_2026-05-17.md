# Goal2222: OptiX PIP One-Pass Compact Experiment

Status: local implementation ready for pod validation.

## Purpose

Goal2219 moved the PIP bottleneck from host exact refinement to the generic two-pass compact-output structure:

- count pass: about `0.033 s`;
- write pass: about `0.033 s`;
- exact refinement: about `0.023 s`.

For sparse positive-hit streams, the count pass is avoidable. Goal2222 adds a one-pass optimistic compact writer with a safe overflow fallback.

## Design

Default positive-only PIP now attempts one compact write pass per chunk:

1. Allocate an optimistic output capacity of at least one row per query point in the chunk.
2. Launch the existing compact writer.
3. Read the atomic output count.
4. If the count fits, download the compact rows and continue.
5. If the count overflows the optimistic capacity, rerun that chunk with exact capacity and keep correctness.

The old two-pass behavior can be forced for diagnosis with:

`RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT=1`

This remains app-agnostic. The rule is based on generic compact-output capacity and overflow fallback, not RayJoin-specific knowledge.

## Claim Boundary

This source change does not authorize a performance claim until pod evidence proves parity and measures the default path.
