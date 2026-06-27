# Call For Review - Phoenix V3 M25 LibRTS AABB OptiX Watch Row

Date: 2026-06-23

Reviewer requested: Claude

Requested verdict label, choose one:

- `accept_closed`
- `accept_with_boundary`
- `partial_not_closed`
- `reject`

## Context

Phoenix V3 is currently in rebuild mode. Do not authorize release unless explicitly stated. Do not introduce V4/external embedding/zero-copy claims. This review concerns one focused blocker only: the M22 LibRTS AABB OptiX watch row.

M22 all-app watch row:

```text
goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index
M22 current/V2.14: 0.803x
threshold: 0.950x
```

M25 did not rerun all-app. It performed a focused same-POD comparison and added a regression test verifying that the current OptiX AABB route uses the productized Phoenix prepared execution/session runner.

Main report:

```text
docs/reports/phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2026-06-23.md
```

Local evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m25_librts_aabb_optix_runner_focused_20260623_124946
```

Relevant test:

```text
tests/v3_phoenix_librts_aabb_count_runner_test.py
```

## Key M25 Results

Same POD:

```text
GPU: NVIDIA RTX 4000 Ada Generation
Driver: 550.127.05
```

Focused results:

| scenario | Current/V2 Embree | Current/V2 OptiX | Current OptiX/Embree |
| --- | ---: | ---: | ---: |
| `m22_exact_2048x1024_r1w0` | 1.093x | 0.922x | 0.095x |
| `repeat50_2048x1024_r50w5` | 0.978x | 0.995x | 105.249x |
| `stress_32768x1024_r20w5` | 0.891x | 0.999x | 63.596x |

Current OptiX field evidence:

```text
prepared_execution_session_runner_used=True
productized_execution_path=prepared_execution_session_runner
primitive_contract=generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count
prepared_query_mode=optix_prepared_query_set
```

## Questions For Review

1. Does M25 close the M22 LibRTS AABB OptiX watch row, or is it only partial evidence?
2. Is `0.922x` on the strict single-shot no-warmup row acceptable under the existing `0.950x` watch threshold?
3. Does the repeat/prepared evidence (`0.995x`, `0.999x`, and 63x-105x OptiX-vs-Embree) justify reclassifying this row as a prepared/repeated Set-A route with a cold single-shot control?
4. Is the new OptiX runner contract test sufficient to prevent regression where current silently bypasses the productized runner?
5. Should the next action be:
   - tune cold/single-shot OptiX path,
   - investigate the Embree 32768 regression,
   - revise scorecard classification,
   - or move to the next Set-A runtime trunk family?
6. Is any public speedup/release wording authorized by this packet?

## Codex Initial Recommendation

`partial_not_closed`

Reason: the focused run proves that current uses the productized runner and that prepared/repeated OptiX behavior is healthy, but the exact strict watch row remains `0.922x`, below the existing `0.950x` threshold. This should not be called closed without an explicit scorecard decision.

## Required Non-Authorization Block

Unless your review explicitly says otherwise, this packet does not authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Hiding the strict single-shot `0.922x` result.
- V4/external zero-copy/embedding claims.
