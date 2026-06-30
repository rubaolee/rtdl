# Goal 417: v0.7 RT DB Conjunctive Scan Python Truth Path

## Goal

Implement the first bounded executable RTDL database-style kernel step in the
Python truth-path runtime.

## Required outcome

- logical database-style input surface needed for bounded `conjunctive_scan`
- a Python truth-path implementation for one bounded conjunctive scan step
- focused tests proving compile plus execution behavior

## Honesty boundary

This goal does not claim:

- oracle/native parity
- PostgreSQL-backed correctness
- backend execution on Embree, OptiX, or Vulkan

This goal is only the Python truth-path closure for bounded
`conjunctive_scan`.
