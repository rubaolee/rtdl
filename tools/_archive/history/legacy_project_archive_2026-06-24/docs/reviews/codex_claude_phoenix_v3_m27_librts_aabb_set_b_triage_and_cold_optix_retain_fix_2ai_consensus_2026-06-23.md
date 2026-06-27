# 2-AI Consensus - Phoenix V3 M27 LibRTS AABB Set-B Triage And Cold OptiX Retain Fix

Date: 2026-06-23

Participants:

- Codex
- Claude

Consensus verdict: **`accept_with_boundary` for the M27 code fix and milestone; watch rows remain open**

## Reviewed Inputs

- `docs/reports/phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_review_2026-06-23.raw.md`
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `tests/v3_phoenix_librts_aabb_count_runner_test.py`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_librts_embree_stress_triage_20260623_130838`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_optix_cold_retain_probe_20260623_131411`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_20260623_131633`
- `docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_extra_20260623_131735`

## Consensus Finding

M27 satisfied its bounded mandate:

1. Embree 32768 stress was triaged with focused POD repeats.
2. The OptiX cold single-shot row received a bounded, generic runner-output-path fix.
3. Local and POD tests passed.
4. No all-app run or release claim was made.

However, M27 does **not** close the Set-B watch rows:

- OptiX cold single-shot is improved, but still has unexplained outliers.
- Embree 32768 is not a deterministic geomean failure, but it is a stability watch blocker.

## Accepted Code Fix

The code fix is accepted and should remain:

```text
query_repeat == 1  -> retain_repeat_outputs=False
query_repeat > 1   -> retain_repeat_outputs=True
```

Reason:

- Retaining tuple outputs for a single measured run is unnecessary overhead.
- Direct runner probe improved median query time from `0.312370911s` to `0.263605766s`.
- Unit tests now cover both single-repeat no-retain and multi-repeat retain behavior.
- The productized runner path remains visible.

Known gap:

- The Embree path still passes `retain_repeat_outputs=True` unconditionally. This is not an M27 blocker, but it must be remembered if future work targets Embree strict cold single-shot rows.

## OptiX Cold Row Status

Post-fix 8-sample strict cold OptiX A/B:

```text
ratios current/V2.14:
0.531x, 1.231x, 1.174x, 1.013x, 0.883x, 0.977x, 1.077x, 1.110x
geomean: 0.973x
median sample ratio: 1.045x
pass count >=0.950x: 6/8
```

Consensus:

- The row is improved.
- The row is **not closed**.
- The sample-1 `0.531x` outlier is severe and must receive a mechanistic explanation attempt before any closure.
- The sample-5 `0.883x` result is a softer but real failure.

Status label:

```text
optix_cold_watch_row_status: improved_not_closed
```

## Embree 32768 Status

Focused triage:

```text
ratios current/V2.14:
1.131x, 0.898x, 0.911x
geomean: 0.975x
```

Consensus:

- Not a deterministic geomean blocker because geomean is above `0.950x`.
- Not explanation-only because current has much higher inter-sample variance than V2.14.
- It must be logged as a stability watch blocker.

Status label:

```text
embree_32768_status: stability_watch_blocker
```

## M28 Permission

M28 may proceed to true Set-A runtime trunk work **only with these constraints**:

1. OptiX cold and Embree 32768 watch rows remain visible and open.
2. Set-A progress must not be used to retroactively close Set-B rows.
3. No release, all-app, public speedup, or broad V3-over-V2 wording is authorized.
4. Before any release packet, both Set-B watch rows must be formally resolved.

Rationale:

- Set-B stability work should not block all Set-A runtime trunk work indefinitely.
- The Phoenix V3 performance source still depends on true Set-A runtime execution, not on endless Set-B cold-row tuning.

## Non-Authorization

This 2-AI consensus does **not** authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Closing the OptiX cold watch row.
- Closing the Embree 32768 stability watch row.
- Hiding OptiX outliers.
- Hiding Embree variance.
- Counting LibRTS AABB single-shot as Set A.
- V4/external zero-copy/embedding claims.

Final status: **M27 code fix accepted; Set-B watch rows remain open; M28 may start true Set-A runtime trunk work under constraints.**
