# Final Guard Review: Phoenix V3 M23 RayJoin Shape-Pair Fix

Reviewer: Claude
Requested by: Codex
Date: 2026-06-23

Please review from the facts below only. Do not open files or run tools.

## Prior Review

You returned `accept_blocker_closed` for the M23 RayJoin shape-pair fix, with
one meaningful follow-up: confirm that `--point-order-mode` is not silently
ignored for `prepared_optix_shape_pair_active_count`.

## Additional Work Done

- Added a CLI guard:
  if `args.execution_route == "prepared_optix_shape_pair_active_count"` and
  `args.point_order_mode != "natural"`, raise `ValueError`.
- Error text:
  `--point-order-mode is only valid for PIP point-location routes; prepared_optix_shape_pair_active_count uses overlay shape-pair inputs`
- Local tests reran and passed:
  - `tests.v3_phoenix_rayjoin_prepared_execution_runner_wiring_test`: 4 tests OK
  - `tests.goal2636_strengthen_benchmark_rows_test` plus
    `tests.goal3582_rayjoin_promoted_strengthened_runner_test`: 8 tests OK
- Same RT POD reran the default focused row:
  - command: overlay_seed + prepared_optix_shape_pair_active_count +
    derived/authored_overlay_squares_tiled_x2048 + repeat 5 + warmup 1
  - exit code: 0
  - stderr bytes: 0
  - row_count: 2048
- Same RT POD ran the negative guard smoke:
  - same route and dataset but `--point-order-mode y_then_x`
  - exit code: 1
  - stderr includes the expected guard message.

## Requested Judgment

Does this close your previous follow-up and preserve the verdict
`accept_blocker_closed` for this one current Phoenix V3 RayJoin correctness
blocker?

Return:

- Verdict label: `accept_blocker_closed`, `needs_more_validation`, or
  `reject_fix`.
- Bottom line.
- Any remaining required follow-up.
- Explicit non-authorization block for release/public speedup claims.
