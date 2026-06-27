# Phoenix V3 M46 LibRTS Set-B Watch Rows Status And Next Protocol

Date: 2026-06-23

Status: `m46_librts_watch_rows_open_protocol_needed_not_release`

This is a read-only status and next-protocol report for the remaining LibRTS
Set-B/control blocker. It does not authorize V3 release, all-app benchmarking,
paid POD spend, public speedup wording, broad V3-over-V2 claims, V4 work,
embedding, C ABI, or true-zero-copy claims.

## Bottom Line

LibRTS remains an open Set-B/control blocker, but it is not a broad OptiX
failure and not a reason to rewrite the AABB engine immediately.

The current correct status is:

```text
LibRTS AABB Set-B watch rows remain open.
M27 code fix is accepted and should stay.
Next work is a focused cold-start/stability protocol, not all-app and not broad
route tuning.
```

## Frozen Scorecard Rows

Frozen all-app rows for `librts_spatial_index`:

| Row | Backend | Set | Frozen V3 vs V2.14 |
| --- | --- | --- | ---: |
| `goal2626_large / librts_embree_aabb_index` | Embree | B | `0.8693053349379956x` |
| `goal2626_large / librts_optix_aabb_index` | OptiX | B | `1.0103352224861961x` |

The frozen Set-B gate therefore has a visible Embree parity/control problem.
Later focused evidence also tracks an OptiX cold single-shot watch row from M25.

## M25 Focused Result

M25 established that the current OptiX path uses the Phoenix productized
prepared-execution/session runner:

```text
prepared_execution_session_runner_used=True
productized_execution_path=prepared_execution_session_runner
primitive_contract=generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count
```

M25 also split the behavior:

| Scenario | Current/V2.14 Embree | Current/V2.14 OptiX |
| --- | ---: | ---: |
| strict cold `2048x1024`, repeat 1, warmup 0 | `1.093x` | `0.922x` |
| prepared repeat50 `2048x1024` | `0.978x` | `0.995x` |
| stress `32768x1024`, repeat20 | `0.891x` | `0.999x` |

Interpretation:

- OptiX prepared/repeated behavior is near parity with V2.14.
- OptiX cold single-shot was below the watch threshold.
- Embree stress showed a real focused regression.

## M27 Accepted Fix And Remaining Watch Rows

M27 code fix:

```text
query_repeat == 1 -> retain_repeat_outputs=False
query_repeat > 1  -> retain_repeat_outputs=True
```

Codex+Claude consensus accepted this code fix with boundary:

```text
docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md
```

Accepted facts:

- The retain fix is generic runner-output-path work.
- It should stay.
- It does not close the watch rows.

Post-fix OptiX cold A/B:

```text
ratios current/V2.14:
0.531x, 1.231x, 1.174x, 1.013x, 0.883x, 0.977x, 1.077x, 1.110x
geomean: 0.973x
median: 1.045x
pass count >=0.950x: 6 / 8
```

Embree 32768 focused triage:

```text
ratios current/V2.14:
1.131x, 0.898x, 0.911x
geomean: 0.975x
median: 0.911x
pass count >=0.950x: 1 / 3
```

Consensus labels:

```text
optix_cold_watch_row_status: improved_not_closed
embree_32768_status: stability_watch_blocker
```

## M31 Existing-Evidence Analysis

M31 re-read the existing M25/M27 evidence without running POD and confirmed:

- The OptiX cold row looks heavily affected by first-sample/cold-start variance.
- Dropping the worst first sample makes OptiX geomean healthy, but a `0.883x`
  sample remains, so the row cannot close.
- Embree geomean is above `0.950x`, but median and 2/3 samples fail, so this
  remains a stability watch blocker.

M31 recommendation:

```text
next LibRTS POD, if authorized later, should be a focused stability protocol:
1. pre-warm process/runtime explicitly;
2. separate first-sample cold-start from steady cold-repeat samples;
3. record current and V2.14 in alternating order to reduce drift;
4. keep OptiX cold single-shot and Embree 32768 stress as Set-B/control watch
   rows, not Set-A runtime-trunk proof.
```

## M46 Classification

```text
active_code_rewrite_target: false
accepted_code_fix_to_keep: M27 retain_repeat_outputs=False for query_repeat == 1
watch_rows_closed: false
next_needed_work: focused stability/cold-start protocol design
paid_pod_authorized_now: false
all_app_authorized_now: false
```

## Next Engineering Recommendation

M47 should prepare, but not run, a focused LibRTS stability protocol packet.

The protocol should:

- alternate V2.14/current execution order;
- separate first-sample cold-start from steady cold-repeat samples;
- include both:
  - OptiX strict cold single-shot `2048x1024`, repeat 1, warmup 0;
  - Embree stress `32768x1024`, repeat 20, warmup 5;
- retain M27's accepted code fix;
- fail closed if stderr, fixture mismatch, runner metadata absence, or row
  contract drift appears;
- report geomean, median, min, pass count, and first-sample-stripped geomean;
- stay classified as Set-B/control evidence, not Set-A runtime-trunk proof.

M47 should not run POD until its protocol receives external review. If the
protocol is accepted, one small focused POD run may be requested later. This
report itself does not authorize that run.

## Non-Authorization

This report does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

## Goal-Level Decision Audit

Decision: keep LibRTS watch rows open, keep the M27 code fix, and make the next
LibRTS action a focused stability/cold-start protocol packet rather than a code
rewrite or all-app run.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   to close LibRTS because geomeans look acceptable, or to rewrite AABB code
   based on cold-start outliers without a stability protocol.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Rerun all-app or run another ad hoc focused POD immediately. Both are
   rejected because the protocol needs to control first-sample and order drift.
4. Can I now try a different path that actually solves the problem? Yes. Write
   M47 as a focused protocol packet, review it externally, then decide whether
   one small POD run is justified.
