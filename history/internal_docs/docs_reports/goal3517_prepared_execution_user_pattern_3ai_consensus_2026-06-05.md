# Goal3517 Prepared Execution User Pattern 3-AI Consensus

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3517 is accepted by Codex, Claude, and Gemini as a narrow prepared-execution
user-pattern and reporting-contract goal. It does not close v2.8, does not
authorize release, and does not authorize public speedup, broad RT-core speedup,
true zero-copy, RayJoin paper reproduction, `rtdl beats RayJoin`, full overlay,
hidden dispatch, hidden partner selection, or app-specific native-engine claims.

## Review Inputs

| Reviewer | Review file | Verdict | Required fixes |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` | `accept-with-boundary` | Two local polish fixes before commit |
| Claude | `docs/reviews/goal3518_claude_review_goal3517_prepared_execution_pattern_2026-06-05.md` | `accept-with-boundary` | Cosmetic claim-boundary wording gap |
| Gemini | `docs/reviews/goal3519_gemini_review_goal3517_prepared_execution_pattern_2026-06-05.md` | `accept-with-boundary` | None |

## Post-Review Fixes Applied

Codex applied two fixes before closing the goal:

- Expanded `PREPARED_EXECUTION_CLAIM_BOUNDARY` to explicitly name RayJoin
  paper-reproduction wording, `rtdl beats RayJoin` wording, and full overlay
  wording, addressing Claude Finding 1.
- Adjusted `PreparedExecutionReport.summary_sec` to avoid double-counting cache
  load/write and warmup inside the setup total. The summary now reports
  `setup`, `warmup`, `steady_state`, and `validation`, while all individual
  phase timings remain available under `phase_timings`.

## Consensus Position

Goal3517 correctly defines:

```text
prepare -> pack/cache -> warm -> run steady-state -> explain timings
```

It exposes setup, cache load/write, warmup count, steady-state stream, planner,
executor, and validation timings without hiding partner/backend choice. It
normalizes existing Goal3511 pod evidence and does not require a fresh pod run
because no measured execution path changed.

Fresh current-HEAD pod confirmation with the inline `prepared_execution_report`
field remains appropriate for Goal3521, the final validation packet.

## Validation

Focused local validation after review fixes:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3517_prepared_execution_user_pattern_test tests.goal3511_overlay_area_steady_state_relation_stream_test tests.goal3509_overlay_area_binary_prepared_payload_cache_test tests.goal3507_overlay_area_prepared_payload_cache_test
```

Result:

```text
Ran 13 tests in 0.010s
OK
```

Compile check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\prepared_execution.py scripts\goal3492_overlay_area_public_cdb_tile_task_executor.py
```

Result: clean.
