# Goal3518 3-AI Consensus: v2.8 Benchmark Matrix Refresh

Date: 2026-06-05

## Scope

Goal3518 added a tested source-of-truth matrix for the promoted v2.8 benchmark apps:

- `src/rtdsl/v2_8_benchmark_matrix.py`
- `tests/goal3518_v2_8_benchmark_matrix_test.py`
- `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`

The matrix covers all 10 promoted apps and uses 12 rows because `spatial_rayjoin` and `raydb_style` each have two distinct benchmark contracts.

## Reviews

| Reviewer | File | Verdict | Notes |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md` plus tests | accept-with-boundary | Internal matrix only; not release authorization. |
| Claude | `docs/reviews/goal3520_claude_review_goal3518_v2_8_benchmark_matrix_2026-06-05.md` | accept | Verified 10-app coverage, 12-row split, timing cells, claim flags, and key numeric copies. |
| Gemini | `docs/reviews/goal3521_gemini_review_goal3518_v2_8_benchmark_matrix_2026-06-05.md` | accept-with-boundary | Accepted the matrix; noted it could not run its own shell test and asked for clearer overlay steady-state arithmetic. |

## Review Intake

Gemini's actionable note was handled after review:

- `spatial_rayjoin_overlay_area_exact_prepared` now spells out the steady-state formula in code notes:
  `0.0038709240034222603 + 0.05171292740851641 + 0.014305617660284042`.
- The Goal3518 report now shows the same formula.
- `tests.goal3518_v2_8_benchmark_matrix_test` now asserts the formula and note text.

Gemini's remaining boundary is procedural: its local tool execution failed, so it manually inspected evidence and relied on Codex's reported test execution for the shell result. This does not invalidate the matrix, but it means the consensus remains an internal engineering consensus, not a release packet.

## Validation

Post-review local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3518_v2_8_benchmark_matrix_test \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test \
  tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test \
  tests.goal3517_prepared_execution_user_pattern_test

Ran 21 tests in 0.010s
OK
```

Additional checks:

- `py -3 -m py_compile src/rtdsl/v2_8_benchmark_matrix.py`
- local scan found no bare `n/a`, placeholder review text in the final reviewed files, or true claim-boundary flags.

## Consensus Verdict

`accept-with-boundary`

Goal3518 is accepted as the internal v2.8 benchmark-app matrix source of truth. It is not a release packet and does not authorize release, public speedup wording, whole-app speedup wording, broad RT-core wording, true-zero-copy wording, paper reproduction claims, hidden partner selection, hidden dispatch, full RayJoin overlay completion claims, or app-specific native-engine behavior.

The next pod-targeted work should refresh the disclosed matrix gaps:

1. phase-separated `robot_collision` timing;
2. phase-separated `contact_manifold` timing;
3. phase-separated `rt_dbscan` preparation/warmup versus grouped-stream tail timing;
4. optional full 12-row current-HEAD matrix packet after the gaps are closed.
