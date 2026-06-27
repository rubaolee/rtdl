# Phoenix V3 M23 RayJoin Shape-Pair Correctness Fix

Status: `focused_correctness_defect_closed_2ai_accept_blocker_closed`

This report records the first M23 repair after the M22 all-app gate failure. It
fixes the current Phoenix V3 RayJoin OptiX crash:

```text
case: rayjoin_optix_promoted_overlay_seed_tiled_x2048
failure_before: TypeError: run_rayjoin_prepared_optix_shape_pair_active_count_workload() got an unexpected keyword argument 'point_order_mode'
fix_scope: remove PIP-only point_order_mode from the shape-pair active-count CLI path
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Why This Was First

The M22 Codex+Claude consensus ranked this current-code correctness defect above
performance regressions. A crashing V3 row can invalidate neighboring timing
interpretation. It must be closed before another all-app POD run.

## Code Change

Changed:

- `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `tests/v3_phoenix_rayjoin_prepared_execution_runner_wiring_test.py`

The direct CLI path for `--execution-route prepared_optix_shape_pair_active_count`
and `--workload overlay_seed` no longer forwards `point_order_mode` to
`run_rayjoin_prepared_optix_shape_pair_active_count_workload()`. That option is
PIP-only and belongs to point-location routes, not overlay shape-pair active
count.

After Claude's first review, a CLI guard was added so non-default point ordering
is not silently ignored:

```text
if execution_route == prepared_optix_shape_pair_active_count
and point_order_mode != natural:
    fail with ValueError
```

The regression test now parses the RayJoin app with AST and verifies every call
to `run_rayjoin_prepared_optix_shape_pair_active_count_workload()` omits
`point_order_mode`. The same test also verifies the CLI guard text exists.

## Local Validation

```text
py -3 -m unittest tests.v3_phoenix_rayjoin_prepared_execution_runner_wiring_test
result: OK, 4 tests

PYTHONPATH=src py -3 -m unittest tests.goal2636_strengthen_benchmark_rows_test tests.goal3582_rayjoin_promoted_strengthened_runner_test
result: OK, 8 tests
```

Note: local Python prints `Could not find platform independent libraries
<prefix>`, but the commands exit successfully. This warning is unrelated to the
RayJoin fix.

## POD Focused Validation

POD:

```text
host: root@213.173.108.14 -p 11592
key: C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
remote_repo: /root/rtdl_v3_rebuild_20260620/current
remote_evidence_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m23_rayjoin_shape_pair_fix_20260623
local_evidence_dir: docs/rebuild/v3/evidence/phoenix_v3_m23_rayjoin_shape_pair_fix_20260623
```

Focused command:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python \
  examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload overlay_seed \
  --execution-route prepared_optix_shape_pair_active_count \
  --dataset derived/authored_overlay_squares_tiled_x2048 \
  --no-rows \
  --repeat 5 \
  --warmup 1
```

Result:

```text
focused_exit_code: 0
stderr_bytes: 0
stdout_json: docs/rebuild/v3/evidence/phoenix_v3_m23_rayjoin_shape_pair_fix_20260623/rayjoin_overlay_seed_shape_pair_x2048.stdout.json
```

Guard smoke:

```text
command_delta: --point-order-mode y_then_x
guard_exit_code: 1
guard_stderr: docs/rebuild/v3/evidence/phoenix_v3_m23_rayjoin_shape_pair_fix_20260623/guard_nondefault_point_order.stderr.txt
expected_error: --point-order-mode is only valid for PIP point-location routes; prepared_optix_shape_pair_active_count uses overlay shape-pair inputs
```

Key output fields:

```text
app: rayjoin_v2_spatial_join
workload: overlay_seed
execution_route: prepared_optix_shape_pair_active_count_device_continuation_reuse
backend: optix
dataset: derived/authored_overlay_squares_tiled_x2048
row_count: 2048
prepared_query_sec: 0.0001560300588607788
prepared_query_sec_total_sec: 0.0007854774594306946
repeat: 5
warmup: 1
summary.output_contract: overlay_active_pair_dependency_count
topology_stream_prepared_handle.query_stream_residency: device_resident_prepared_left_shape_set_with_reusable_active_count_executor
```

Claim flags remain false:

```text
full_rayjoin_reproduction: false
paper_scale_perf_claim_authorized: false
public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
true_zero_copy_claim_authorized: false
whole_app_speedup_claim_authorized: false
```

## Interpretation

The M22 current Phoenix V3 correctness defect for this row is closed: the row no
longer crashes with an unexpected `point_order_mode` argument and runs to
completion on the same RT POD.

This does not change the M22 release verdict. Phoenix V3 is still blocked by the
M21/M22 all-app result: 1.049x overall geomean, Set-A 1.013x, Barnes-Hut 0.831x,
LibRTS OptiX AABB watch row 0.803x, and V2.14 baseline failures.

## Next Work

1. Request Claude review of this focused fix and evidence.
2. Mark the RayJoin current-code correctness blocker closed.
3. Move to the next blocker: Barnes-Hut severe regression.
4. Do not rerun all-app until the remaining blockers are closed.

## 2-AI Review

Claude returned `accept_blocker_closed` twice:

```text
first_review: docs/reviews/claude_phoenix_v3_m23_rayjoin_shape_pair_fix_review_2026-06-23.raw.md
first_review_follow_up: add guard for non-default point_order_mode on shape-pair route
final_guard_review: docs/reviews/claude_phoenix_v3_m23_rayjoin_shape_pair_fix_final_guard_review_2026-06-23.raw.md
final_verdict: accept_blocker_closed
remaining_required_follow_up_for_this_blocker: none
```

Consensus:

```text
codex_claude_consensus: docs/reviews/codex_claude_phoenix_v3_m23_rayjoin_shape_pair_fix_2ai_consensus_2026-06-23.md
release_authorized_by_consensus: false
public_speedup_claim_authorized_by_consensus: false
broad_v3_faster_than_v2_claim_authorized_by_consensus: false
```

## Goal-Level Decision Audit

1. Was I foolish?

No for this fix. The action was a minimal correctness repair on a V3 code defect
identified by the M22 gate and Claude review.

2. If yes, what actions made the decision foolish?

No new foolish action is recorded. The risky action would have been to convert
this focused success into a release or speedup claim.

3. Was there another path?

Yes. I could have skipped this row and worked on Barnes-Hut first. That would
leave a known V3 crash in the benchmark surface and keep future all-app evidence
invalid.

4. Can I now try a different path?

Yes. After external review, the path moves to Barnes-Hut regression and LibRTS
watch-row repair, not another all-app run.
