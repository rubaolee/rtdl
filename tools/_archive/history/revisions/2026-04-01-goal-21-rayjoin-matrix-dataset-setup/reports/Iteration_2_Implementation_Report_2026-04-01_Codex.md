# Goal 21 Iteration 2 Implementation Report

## Summary

Goal 21 has been implemented as a frozen planning/data contract for the Embree RayJoin reproduction program.

## Deliverables Added

### Program document

- [embree_rayjoin_reproduction_program.md](/Users/rl2025/rtdl_python_only/docs/embree_rayjoin_reproduction_program.md)

This defines the three-goal program:

- Goal 21: matrix and dataset setup
- Goal 22: workload/runtime gap closure
- Goal 23: bounded local reproduction runs

### Goal 21 setup document

- [goal_21_rayjoin_matrix_dataset_setup.md](/Users/rl2025/rtdl_python_only/docs/goal_21_rayjoin_matrix_dataset_setup.md)

This defines the acceptance bar for the setup goal itself.

### Frozen Goal 21 matrix and profile document

- [goal_21_rayjoin_matrix_dataset_frozen.md](/Users/rl2025/rtdl_python_only/docs/goal_21_rayjoin_matrix_dataset_frozen.md)

This freezes:

- paper artifact mapping,
- dataset family status,
- fidelity labels,
- local reduced-size runtime profiles,
- and the blocker handoff to Goal 22.

## Main Frozen Decisions

1. The paper-target artifacts are:
   - Table 3
   - Figure 13
   - Figure 14
   - Table 4
   - Figure 15

2. Figure 13 and Figure 14 remain `synthetic-input` local analogues for the Embree phase.

3. Table 3 / Table 4 / Figure 15 require real dataset acquisition or deterministic derivation work before execution.

4. `overlay` remains an `overlay-seed analogue` workload in the Embree phase and must be labeled that way in later reports.

5. The reduced local profile policy is now frozen:
   - `lsi`: `R = 100,000`, `S = 100,000..500,000`
   - `pip`: `R = 100,000`, `S = 2,000..10,000`
   - Table 3 and overlay cases must define bounded per-pair local profiles in Goal 22 before execution.

## Goal 22 Handoff

Goal 22 is now constrained to the blocker list in the frozen Goal 21 document, especially:

- dataset acquisition/conversion for the missing paper families
- explicit Table 3 / Table 4 / Figure 15 generators
- a final reporting structure that distinguishes exact, derived, synthetic, and overlay-seed analogue outputs
