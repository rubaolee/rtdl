# Goal 22 Spec

## Title

RayJoin Embree Gap Closure

## Motivation

Goal 21 froze the paper artifact matrix, dataset status, local runtime policies, and the blocker list. Goal 22 exists to close those blockers without re-opening planning scope.

## Goal

Implement the missing dataset/provenance/reporting machinery required to support the bounded local RayJoin-on-Embree reproduction package.

## Frozen Inputs

- [goal_21_rayjoin_matrix_dataset_frozen.md](/Users/rl2025/rtdl_python_only/docs/goal_21_rayjoin_matrix_dataset_frozen.md)
- Goal 21 blocker list

## Initial Scope

The first Goal 22 slice should focus on:

1. a machine-readable paper-target registry
2. a machine-readable dataset-family registry
3. a machine-readable local-profile registry
4. generator support for:
   - Table 3 analogue
   - Table 4 analogue
   - Figure 15 analogue
5. report metadata that carries fidelity labels and the overlay-seed analogue boundary

Dataset acquisition helpers may be added if they can be done cleanly in the same slice.

## Acceptance Bar

1. Goal 22 addresses only blockers named by Goal 21
2. the generator/reporting path for Table 3 / Table 4 / Figure 15 exists
3. fidelity and overlay-seed labels are preserved in outputs
4. Gemini approves the implementation and Claude agrees the accepted blockers for this slice are resolved
