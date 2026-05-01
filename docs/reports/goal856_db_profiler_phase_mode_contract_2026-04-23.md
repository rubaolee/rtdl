# Goal856: DB Profiler Phase-Mode Contract

Date: 2026-04-23

Status: implemented locally

## Problem

Goals850 and 851 removed grouped row materialization from the OptiX
`compact_summary` DB paths, but the profiler contract still described DB run
phases generically as `query_*_and_materialize_sec`.

That would make the next RTX artifact harder to interpret, because the DB app
would have a faster grouped-summary path while the profiler vocabulary still
implied row materialization.

## Change

Updated the DB prepared-session profiler to emit:

- `reported_run_phase_modes`

Per section, this classifies:

- `scan` as `count_summary` or `row_materializing`
- `grouped_count` as `group_summary` or `row_materializing`
- `grouped_sum` as `group_summary` or `row_materializing`

The phase contract text now explicitly says:

- grouped compact-summary fast paths use `query_*_summary_sec`
- row-returning paths use `query_*_and_materialize_sec`

The internal Goal847 review note for `database_analytics` also now states that
Goals850/851 reduced grouped row materialization locally and that a fresh RTX
rerun is required before that reduction appears in the active review package.

## Files

- `/Users/rl2025/rtdl_python_only/scripts/goal756_db_prepared_session_perf.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal847_active_rtx_claim_review_package.py`
- `/Users/rl2025/rtdl_python_only/tests/goal756_db_prepared_session_perf_test.py`

## Boundary

This is a reporting-contract improvement only. It does not by itself change
performance, authorize a new RTX claim, or promote `database_analytics` to
`rt_core_ready`.
