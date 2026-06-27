# Call For Review: Phoenix V3 M28 Set-A Runtime-Trunk Family Freeze

Date: 2026-06-23

Please critically review this Phoenix V3 M28 freeze packet:

`docs/rebuild/v3/phoenix_v3_m28_set_a_trunk_family_freeze_aggregate_tree_fused_vector_sum_2026-06-23.md`

## Requested Verdict Labels

Use exactly one:

- `approve_family_freeze`
- `approve_with_amendments`
- `blocked_needs_revision`
- `reject_wrong_family`

## Context

Phoenix V3 is blocked until runtime-sourced, productized, app-agnostic Set-A
evidence exists. All-app runs remain forbidden until at least two true Set-A
families are accepted.

Prior evidence:

- RTDBSCAN productized runner recovered only to parity, about `0.9976x`, after
  an earlier severe loss.
- RayJoin has structural runner evidence but no material runtime-sourced win.
- Barnes-Hut aggregate-tree fused weighted-vector sum already has a focused POD
  A/B:
  `docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718/`
- Report:
  `docs/reports/phoenix_v3_step1_barnes_hut_runner_parity_pod_ab_2026-06-22.md`
- Prior fixed-implementation review:
  `docs/reviews/second_ai_phoenix_v3_barnes_hut_runner_fixed_review_2026-06-22.md`

The M28 proposal freezes Barnes-Hut aggregate-tree fused weighted-vector sum as
the first Set-A runtime-trunk family, but it tries to avoid overclaiming:

- current runner vs current fused control is a productized-runner parity gate;
- historical prepared OptiX/frontier displacement is a no-go route reference,
  not a public claim;
- v2.14/current comparison must be freshly classified in M29 because local tag
  inspection suggests v2.14 has CPU fused and grouped-stream pieces, but lacks
  the current Numba CUDA fused/runner modes.

## Questions

1. Is Barnes-Hut aggregate-tree fused weighted-vector sum the right first true
   Set-A family to freeze, given the RTDBSCAN/RayJoin history?
2. Are the proposed gates sufficient to prove that the productized V3 runtime
   trunk actually executes and preserves internal residency?
3. Is the V2.14/current boundary honest enough, especially the warning that
   v2.14 node-coverage and current fused force-vector continuation are not the
   same contract?
4. Is the current-runner vs current-fused-control parity bar (`>=0.95x` every
   row, geomean `>=0.98x`) strict enough for runner productization?
5. Is the material-gain floor (`>=1.15x`, preferred `>=1.20x`) appropriate for
   any speed classification?
6. Are there hidden app-specific, RT-core, zero-copy, or V4 overclaims in the
   freeze packet?
7. Should M29 proceed as written, or should the family choice be revised before
   spending more POD time?

## Required Output

Save your review to:

`docs/reviews/claude_phoenix_v3_m28_set_a_trunk_family_freeze_review_2026-06-23.raw.md`

Include:

- one verdict label;
- blocking findings, if any;
- required amendments, if any;
- explicit answers to the seven questions;
- a non-authorization block stating that your review authorizes no release, no
  all-app run, no public speedup claim, no broad V3-over-V2 claim, no RT-core
  speedup claim, no true-zero-copy claim, and no V4 work.
