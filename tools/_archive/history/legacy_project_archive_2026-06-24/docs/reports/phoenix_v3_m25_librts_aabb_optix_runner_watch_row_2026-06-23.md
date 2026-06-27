# Phoenix V3 M25 - LibRTS AABB OptiX Watch Row Focused Result

Date: 2026-06-23

Status: **focused evidence partial, strict watch row not closed**

This packet investigates the M22 all-app watch alert:

| M22 watch row | M22 current / V2.14 | threshold | action |
| --- | ---: | ---: | --- |
| `goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index` | `0.803x` | `0.950x` | flag and report without rationalization |

M25 does **not** run all-app. It performs a focused same-POD V2.14/current comparison for LibRTS AABB count routes, checks whether the current tree actually uses the Phoenix prepared execution/session runner, and separates cold single-shot behavior from prepared/repeated behavior.

## Decision Audit

1. Was the M25 blocker choice foolish?
   No. The selected row is a current-route NVIDIA RT performance watch row from M22 and directly matches the Phoenix V3 priority.

2. If yes, what actions made it foolish?
   Not applicable. M25 avoided the foolish path of rerunning all-app before understanding the focused blocker.

3. Was there another path?
   Yes. The next path could have been remaining correctness failures. I chose this row first because it is a current-route RT-performance blocker, not a legacy V2.14-only failure.

4. Can I now try a different path?
   Yes. If the strict single-shot threshold remains controlling, the next path is cold/hot split tuning for OptiX AABB or scorecard reclassification. If prepared/repeated Set-A behavior is accepted as the relevant V3 path, the next path is the remaining Embree large regression or the next Set-A runtime trunk family.

## Evidence

POD:

```text
root@213.173.108.14 -p 11592
GPU: NVIDIA RTX 4000 Ada Generation
Driver: 550.127.05
```

Remote artifact:

```text
/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m25_librts_aabb_optix_runner_focused_20260623_124946
```

Local evidence copy:

```text
docs/rebuild/v3/evidence/phoenix_v3_m25_librts_aabb_optix_runner_focused_20260623_124946
```

Environment hashes:

```text
current_sha256_prepared_execution=114cdbdfea892484047d55ddd306269bf13dcb5c43b092c9b219b469f0b0647c
current_sha256_librts_app=29ab15534a6df96ba877b498eedc690c4fc39640159a1db9144adbded93dbd83
v2_14_sha256_librts_app=e81fc79b714f51ed1f5ce1a6b50bb8cda5639e267552b8b41f97a004c3c676ad
```

Stderr files for the 12 focused runs are empty.

## What Changed In This M25 Step

M25 added a regression test proving that the current LibRTS OptiX AABB prepared query route calls the productized Phoenix prepared execution/session runner:

```text
tests/v3_phoenix_librts_aabb_count_runner_test.py
```

The test checks:

- `run_optix_aabb_counts(... prepared_queries=True ...)` calls `run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session`.
- The call uses explicit backend/partner/device semantics: `operation="all"`, `partner="none"`, `device="cuda:0"`.
- The payload records:
  - `prepared_execution_session_runner_used=True`
  - `productized_execution_path="prepared_execution_session_runner"`
  - `primitive_contract="generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count"`
  - `prepared_query_mode="optix_prepared_query_set"`
  - release and public speedup claims remain unauthorized.

## Tests

Local:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test

42 tests OK
```

POD:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python -m unittest \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test

42 tests OK
```

## Focused Same-POD Results

Metric: median measured query seconds from each app payload's `repeat_protocol.query_sec_median`.

| scenario | V2.14 Embree sec | Current Embree sec | Current/V2 Embree | V2.14 OptiX sec | Current OptiX sec | Current/V2 OptiX | V2.14 OptiX/Embree | Current OptiX/Embree |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `m22_exact_2048x1024_r1w0` | 0.031180210 | 0.028527565 | 1.093x | 0.276456766 | 0.299728468 | 0.922x | 0.113x | 0.095x |
| `repeat50_2048x1024_r50w5` | 0.097765107 | 0.099954136 | 0.978x | 0.000944939 | 0.000949692 | 0.995x | 103.462x | 105.249x |
| `stress_32768x1024_r20w5` | 0.895755075 | 1.005517442 | 0.891x | 0.015789419 | 0.015811000 | 0.999x | 56.731x | 63.596x |

## Field-Level Runner Evidence

Current OptiX payloads all include:

```text
prepared_execution_session_runner_used=True
productized_execution_path=prepared_execution_session_runner
primitive_contract=generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count
prepared_query_mode=optix_prepared_query_set
```

V2.14 payloads do not contain the Phoenix runner fields.

This means the focused current run is not silently bypassing the productized runner.

## Interpretation

M25 explains the misleading shape of the old "OptiX is absurdly slow" impression:

- The strict M22 exact row is a **single measured query with no warmup**. On that row, current OptiX is still below the 0.950x watch threshold at `0.922x`.
- With prepared/repeated execution and warmup, current OptiX is effectively parity with V2.14: `0.995x` for repeat50 and `0.999x` for the larger 32768-box stress case.
- In prepared/hot behavior, OptiX is not slow versus Embree. It is `105.249x` faster than current Embree in repeat50 and `63.596x` faster in the 32768-box stress case.
- The remaining current/V2 gap is not a broad OptiX failure. It is a cold/single-shot watch-row failure plus an unresolved Embree large-case regression.

The strict row should **not** be declared closed unless the release bar accepts a cold/hot split where the single-shot no-warmup row is a control/explanation row and the prepared/repeated row is the V3 Set-A route.

## Open Blockers

1. **Strict OptiX watch row remains below threshold.**
   The exact M22-style current/V2 OptiX row is `0.922x`, below `0.950x`.

2. **Current Embree large stress row regresses.**
   The 32768-box current/V2 Embree row is `0.891x`. This is not the original OptiX watch row, but it is a real focused regression.

3. **Release bar classification is still controlling.**
   If LibRTS AABB count is classified as single-shot Set-B/control, it needs parity plus explanation. If classified as prepared/repeated Set-A, the hot/repeated route has evidence, but the strict cold row still needs documented boundary text.

## Non-Authorization

This packet does not authorize:

- V3 release.
- A full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Hiding the strict single-shot `0.922x` result.
- Treating this as a V4/external zero-copy/embedding result.

## Recommended Next Step

Ask for external review on the exact status label:

- If reviewers require strict watch-row parity, M25 status should be **partial_not_closed**, and the next engineering step is cold first-query tuning or a scorecard adjustment.
- If reviewers accept the V3 prepared/repeated route as the controlling user path, M25 can be accepted as **watch row explained with boundary**, but not as an unconditional speedup closure.

Codex recommendation before external review: **partial_not_closed**.
