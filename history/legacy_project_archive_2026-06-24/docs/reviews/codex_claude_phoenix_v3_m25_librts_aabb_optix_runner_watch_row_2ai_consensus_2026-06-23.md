# 2-AI Consensus - Phoenix V3 M25 LibRTS AABB OptiX Watch Row

Date: 2026-06-23

Participants:

- Codex
- Claude

Consensus verdict: **`partial_not_closed`**

## Reviewed Inputs

- `docs/reviews/call_for_review_phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2026-06-23.md`
- `docs/reports/phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m25_librts_aabb_optix_runner_watch_row_review_2026-06-23.raw.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m25_librts_aabb_optix_runner_focused_20260623_124946`
- `tests/v3_phoenix_librts_aabb_count_runner_test.py`

## Consensus Finding

M25 is accepted as a focused investigation and evidence packet, but **it does not close the M22 LibRTS AABB OptiX watch row**.

The decisive reason is simple:

```text
strict watch threshold: 0.950x
M25 strict single-shot current/V2.14 OptiX result: 0.922x
```

`0.922x` is improved from M22's `0.803x`, but it remains below threshold. Understanding the gap does not close the gap.

## What M25 Did Establish

Both reviewers agree that M25 established real progress:

- Current OptiX AABB count route now has field evidence of the productized Phoenix prepared execution/session runner:
  - `prepared_execution_session_runner_used=True`
  - `productized_execution_path=prepared_execution_session_runner`
  - `primitive_contract=generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count`
  - `prepared_query_mode=optix_prepared_query_set`
- The new unit test is a valid regression guard against silently bypassing the OptiX runner route.
- Prepared/repeated OptiX behavior is healthy:
  - `repeat50_2048x1024_r50w5`: current/V2.14 OptiX `0.995x`
  - `stress_32768x1024_r20w5`: current/V2.14 OptiX `0.999x`
  - current OptiX vs current Embree: `105.249x` and `63.596x` for the repeated/stress rows.
- The focused POD run was clean:
  - same POD
  - same GPU
  - all 12 runs completed
  - stderr files empty
  - environment hashes recorded

## What M25 Did Not Establish

Both reviewers agree that M25 did not establish:

- V3 release readiness.
- Full all-app readiness.
- Public speedup wording.
- Broad "V3 faster than V2.x" wording.
- Closure of the strict M22 OptiX watch row.
- Permission to hide or soften the `0.922x` single-shot result.

## New Open Blocker

M25 also revealed a separate current Embree large-case regression:

```text
scenario: stress_32768x1024_r20w5
current/V2.14 Embree: 0.891x
```

This is not the original OptiX watch row, but it must be logged as an open Phoenix V3 performance blocker.

## Required Next Decision

The next step should be a scorecard classification decision before more engineering work:

1. If the strict single-shot no-warmup row remains the controlling release metric, the next engineering goal must tune or simplify the cold first-query OptiX path until it reaches at least `0.950x`.
2. If the V3 user path is defined as prepared/repeated execution, the scorecard must explicitly reclassify LibRTS AABB as a prepared/repeated Set-A route and retain single-shot cold behavior as a boundary/control row.

Without this decision, further work risks optimizing the wrong metric.

## Non-Authorization

This 2-AI consensus does **not** authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Treating M25 as a closed release blocker.
- Treating M25 as V4/external zero-copy/embedding evidence.

Final status: **M25 evidence complete; blocker not closed; scorecard classification decision required before next engineering step.**
