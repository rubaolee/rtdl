# Call For Review: Phoenix V3 M23 RayJoin Shape-Pair Fix

Reviewer: Claude
Requested by: Codex
Date: 2026-06-23

Please review from the facts below only. Do not open files or run tools.

## Facts

- M22 failed current Phoenix V3 row:
  `rayjoin_optix_promoted_overlay_seed_tiled_x2048`
- Failure:
  `TypeError: run_rayjoin_prepared_optix_shape_pair_active_count_workload() got an unexpected keyword argument 'point_order_mode'`
- Root cause:
  the direct CLI path for `--execution-route prepared_optix_shape_pair_active_count`
  and `--workload overlay_seed` passed PIP-only `point_order_mode` into the
  overlay shape-pair active-count workload function.
- Fix:
  remove `point_order_mode=args.point_order_mode` from that call.
- Regression test:
  AST scan verifies every call to
  `run_rayjoin_prepared_optix_shape_pair_active_count_workload()` omits
  `point_order_mode`.
- Local tests:
  - `py -3 -m unittest tests.v3_phoenix_rayjoin_prepared_execution_runner_wiring_test`
    passed, 4 tests.
  - `PYTHONPATH=src py -3 -m unittest tests.goal2636_strengthen_benchmark_rows_test tests.goal3582_rayjoin_promoted_strengthened_runner_test`
    passed, 8 tests.
- POD:
  - same RT hardware at `root@213.173.108.14 -p 11592`
  - key `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
  - remote repo `/root/rtdl_v3_rebuild_20260620/current`
- Focused command:
  `PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload overlay_seed --execution-route prepared_optix_shape_pair_active_count --dataset derived/authored_overlay_squares_tiled_x2048 --no-rows --repeat 5 --warmup 1`
- Focused POD result:
  - exit code: 0
  - stderr: 0 bytes
  - row_count: 2048
  - prepared_query_sec: 0.0001560300588607788
  - prepared_query_sec_total_sec: 0.0007854774594306946
  - repeat: 5
  - warmup: 1
  - output contract: `overlay_active_pair_dependency_count`
  - query stream residency:
    `device_resident_prepared_left_shape_set_with_reusable_active_count_executor`
- Claim flags remain false:
  - release authorized: false
  - public speedup claim authorized: false
  - broad V3 faster than V2.x claim authorized: false
  - full RayJoin reproduction: false
  - RTDL beats RayJoin: false

## Requested Judgment

1. Is it valid to mark this one current Phoenix V3 RayJoin correctness blocker as
   closed?
2. Is the fix appropriately narrow, or does it look like app-specific tuning?
3. Does this evidence change the M22 non-release verdict?
4. What should be the next blocker after this fix?

## Required Output

Return:

- Verdict label: `accept_blocker_closed`, `needs_more_validation`,
  `reject_fix`, or `release_ready`.
- Bottom line.
- Findings ordered by severity.
- Required follow-up if any.
- Explicit non-authorization block for release/public claims.
