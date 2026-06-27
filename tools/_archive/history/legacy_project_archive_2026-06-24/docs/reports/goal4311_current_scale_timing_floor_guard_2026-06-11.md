# Goal4311: Current Scale-Profile Timing-Floor Guard

Date: 2026-06-11

## Verdict

`accept-with-boundary` for closing the first no-pod slice of Claude Fable5 P5.

Goal4266 already established the right reader-facing timing rule for partner
comparison rows: do not publish decision-grade performance conclusions from
subsecond hot totals. Fable5 correctly observed that the main ten-app
scale-profile runner did not yet expose that rule per row.

Goal4311 adds that exposure to the current scale-profile runner without
rerunning pod evidence and without changing any old artifact.

## What Changed

`scripts/goal3828_current_benchmark_scale_profile_runner.py` now emits:

- `hot_path_floor_evaluation` on each row;
- `hot_path_floor_summary` at packet level;
- an explicit status for rows without a numeric internal floor:
  `smoke_scale_or_internal_not_claim_grade`;
- an explicit status for rows with an internal floor but a short observed
  duration: `subfloor_not_claim_grade`;
- an explicit status for rows whose metric path fails to resolve to a numeric
  scalar: `metric_not_numeric`.
- an auxiliary `metric_resolution_status` that distinguishes
  `metric_numeric`, `metric_not_numeric`, `metric_path_missing`, and
  `stdout_json_missing_or_unparseable` while preserving the claim-blocking
  `metric_not_numeric` row status.

Dry-run packets now show the intended floor policy before a pod is used. Runtime
packets evaluate the declared `representative_hot_path_metric` path against the
row JSON payload and compare it to `hot_path_duration_target_sec` when that
target exists.

After Claude Goal4312 review, dry-run packet summaries now use
`dry_run_policy_only_no_runtime_evaluation` instead of the generic `accept`
status. This keeps pre-pod policy checks visibly separate from runtime
floor-met evidence.

The current registry has two floor-targeted rows:

- `robot_collision_optix_scale_default_1024_no_probe_reference`
- `raydb_style_optix_count_scale_default_262k`

Rows without a target stay usable as coverage, smoke, or internal diagnostic
rows, but not as decision-grade performance evidence.

## Boundary

Goal4311 does not authorize release, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.

It also does not claim that the historical Goal4215 packet met the new
per-row floor. The next pod refresh must produce a fresh packet with these
fields populated before any reader treats the ten-app scale profile as
floor-aware evidence.

## Validation

Dry-run artifact:

`docs/reports/goal4311_current_scale_timing_floor_guard_dry_run.json`

Focused Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4311_current_scale_timing_floor_guard_test
```

The test covers:

- floor-met runtime evaluation;
- subfloor runtime evaluation;
- non-numeric metric-path rejection;
- metric-path missing versus stdout-missing resolution metadata;
- smoke/internal row labeling;
- dry-run packet exposure for all ten rows;
- dry-run summary status that cannot be mistaken for runtime floor success;
- packet-level summary behavior.

## Next Pod Need

The next pod-required step is a fresh ten-app scale-profile packet with the
updated runner. The desired result is not necessarily that every row meets a
floor; the desired result is that every row is visibly classified as
floor-met, subfloor/not-claim-grade, or smoke/internal.
