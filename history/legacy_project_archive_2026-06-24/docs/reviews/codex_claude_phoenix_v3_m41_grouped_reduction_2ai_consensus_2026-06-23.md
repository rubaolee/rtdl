# Codex + Claude 2-AI Consensus: Phoenix V3 M41 Grouped Reduction

Date: 2026-06-23

Consensus verdict: `m41_contract_positive_performance_blocked_paid_pod_blocked`

## Inputs

M41 local harness:

- `docs/reports/phoenix_v3_m41_grouped_reduction_second_family_local_harness_2026-06-23.md`
- `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`
- `tests/v3_phoenix_m41_grouped_reduction_harness_test.py`

Claude local harness review:

- `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_second_family_local_harness_recorded_review_2026-06-23.md`

Small local CUDA smoke:

- `docs/reports/phoenix_v3_m41_grouped_reduction_local_cuda_smoke_intake_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_local_cuda_smoke_recorded_review_2026-06-23.md`

Serious free local result:

- `docs/reports/phoenix_v3_m41_grouped_reduction_serious_free_local_intake_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_serious_after_warmupfix_20260623_150500/summary.json`
- `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_serious_free_local_recorded_review_2026-06-23.md`

Validation:

- focused M41/release tests: 9 tests OK
- full `v3_rebuild`: 120 modules / 626 tests in 77.865s OK
- stdout:
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_serious_local_20260623_150330.stdout.txt`

## Consensus

Codex and Claude agree:

- M41 selected a valid second generic family: `grouped_vector_sum_2d`.
- The productized prepared-execution runner executes correctly at serious
  free-local scale.
- The grouped-reduction contract path is positive.
- The grouped-reduction performance path is blocked for paid POD.
- No public speedup, release, all-app, or broad V3-over-V2 claim is authorized.

Performance facts:

- runner vs legacy hot: `3.456135x`
- runner vs legacy wall: `52.823894x`
- runner vs CPU hot: `0.4979998501868343x`

The runner-vs-CPU hot inversion is a hard block for paid POD. The likely cause
is low occupancy: Numba reported `grid size 4`.

## Decision

Close M41 as:

```text
contract-positive, performance-blocked
```

Do not spend paid POD on grouped reduction now.

Next work must choose one path:

- Path A: diagnose the grid-size/occupancy root cause, then run at most one
  bounded free-local shape experiment if the diagnosis supports it; or
- Path B: move Step-2 performance evidence to another family.

## Goal-Level Decision Audit

1. Was I foolish?

   No. The decision accepts good contract evidence while blocking paid spend
   because the CPU-hot result is adverse.

2. If yes, what actions made the decision foolish?

   The foolish action would be highlighting runner-vs-legacy `3.456x` while
   hiding runner-vs-CPU `0.498x`, then asking for paid POD.

3. Was there another path?

   Yes. Continue grouped-reduction experiments blindly. Claude explicitly
   rejected that before grid-size root-cause diagnosis.

4. Can I now try a different path that actually solves the problem?

   Yes. Either diagnose occupancy with a bounded local experiment, or select a
   different Step-2 performance family. Both avoid paid-POD waste.

## Non-Authorization Block

This consensus does not authorize release, all-app POD spend, paid focused POD
spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy claims,
or broad V3-over-V2 claims.
