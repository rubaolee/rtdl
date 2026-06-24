# Goal 23: Bounded Embree Reproduction Runs

## Goal

Execute the currently runnable RayJoin-on-Embree reproduction package under the frozen `5-10 minute` local policy and generate the corresponding tables, figures, and final report.

## Scope

Goal 23 is an execution/reporting goal, not a new workload-design goal.

It may include:

- bounded local runs for all currently runnable paper-target analogues,
- partial Table 3 generation with explicit missing rows for not-yet-acquired families,
- Figure 13 / Figure 14 bounded reruns under the frozen Goal 21 profiles,
- Table 4 / Figure 15 overlay-seed analogue generation from bounded local runs,
- a final Embree reproduction report that distinguishes:
  - exact-input,
  - derived-input,
  - fixture-subset,
  - synthetic-input,
  - and missing/unacquired rows.

## Non-Goals

Goal 23 does not include:

- pretending missing paper datasets are already acquired,
- changing the frozen Goal 21 matrix,
- adding unrelated new workloads,
- changing the NVIDIA roadmap.

## Accepted Execution Boundary

The current executable slice is:

- Table 3: partial bounded local rows only for dataset families that are already executable locally,
- Figure 13: full bounded local synthetic analogue,
- Figure 14: full bounded local synthetic analogue,
- Table 4: bounded overlay-seed analogue,
- Figure 15: bounded overlay-seed speedup analogue.

The final report must state clearly which rows are executed and which remain blocked on dataset acquisition.

## Acceptance Bar

Goal 23 is complete when:

1. the bounded local runnable slice is executed successfully,
2. table/figure artifacts are generated automatically,
3. the final report labels missing families honestly,
4. Gemini accepts the implemented slice,
5. Claude accepts the goal-level closure.
