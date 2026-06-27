# Codex + Claude 2-AI Consensus: Phoenix V3 M23 RayJoin Shape-Pair Fix

Date: 2026-06-23

## Inputs

- Codex report:
  `docs/reports/phoenix_v3_m23_rayjoin_shape_pair_fix_2026-06-23.md`
- Evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m23_rayjoin_shape_pair_fix_20260623/`
- Claude first review:
  `docs/reviews/claude_phoenix_v3_m23_rayjoin_shape_pair_fix_review_2026-06-23.raw.md`
- Claude final guard review:
  `docs/reviews/claude_phoenix_v3_m23_rayjoin_shape_pair_fix_final_guard_review_2026-06-23.raw.md`

## Shared Verdict

Verdict: `accept_blocker_closed`

Codex and Claude agree that the specific current Phoenix V3 RayJoin correctness
blocker from M22 is closed:

```text
row: rayjoin_optix_promoted_overlay_seed_tiled_x2048
previous_failure: unexpected point_order_mode argument
focused_pod_default_exit_code: 0
focused_pod_default_stderr_bytes: 0
focused_pod_guard_exit_code_for_nondefault_point_order: 1
guard_error_expected: true
```

## What Changed

1. The shape-pair active-count CLI path no longer forwards PIP-only
   `point_order_mode` into
   `run_rayjoin_prepared_optix_shape_pair_active_count_workload()`.

2. A CLI guard now rejects non-default point order for
   `prepared_optix_shape_pair_active_count`, avoiding silent argument discard.

3. Local regression tests pass:
   `tests.v3_phoenix_rayjoin_prepared_execution_runner_wiring_test`,
   `tests.goal2636_strengthen_benchmark_rows_test`, and
   `tests.goal3582_rayjoin_promoted_strengthened_runner_test`.

4. Same-RT-POD validation passes for the default row and fails as expected for
   the invalid non-default point-order combination.

## Non-Authorization

Release is not authorized.

Public speedup claims are not authorized.

Broad "V3 is faster than V2.x" claims are not authorized.

Full RayJoin reproduction and "RTDL beats RayJoin" claims are not authorized.

This consensus closes one correctness blocker only. The M22 release verdict
remains blocked because the all-app gate still has Barnes-Hut severe regression,
Set-A flat geomean, LibRTS OptiX watch-row regression, and V2.14 baseline
failures.

## Next Blocker

Move to Barnes-Hut severe regression:

```text
app_geomean: 0.831x
protocol_floor: 0.900x
priority: release-blocking severe regression
recommended_scope: focused Barnes-Hut probes before any all-app rerun
```

## Goal-Level Decision Audit

1. Was I foolish?

No for accepting this blocker closure. The closure is backed by local tests,
same-RT-POD positive validation, same-RT-POD negative guard validation, and
Claude review.

2. If yes, what actions made the decision foolish?

No new foolish action is recorded. It would be foolish to generalize this row
closure into a V3 release or broad performance claim; this file explicitly
forbids that.

3. Was there another path?

Yes. I could have stopped after the first Claude acceptance without adding the
guard. That would leave a silent CLI trap. The guard path is stronger.

4. Can I now try a different path?

Yes. The correct next path is Barnes-Hut regression repair, not all-app rerun.
