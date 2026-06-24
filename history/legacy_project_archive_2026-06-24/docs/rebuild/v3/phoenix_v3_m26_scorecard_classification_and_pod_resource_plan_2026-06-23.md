# Phoenix V3 M26 - Scorecard Classification And POD Resource Plan

Date: 2026-06-23

Status: **proposed plan pending external review**

Purpose: convert the M25 `partial_not_closed` result into a controlled project plan, so POD time is spent on the runtime trunk and not on another all-app run before the architecture can win.

## Starting Facts

M25 2-AI consensus:

```text
verdict: partial_not_closed
strict watch threshold: 0.950x
M25 strict single-shot current/V2.14 OptiX: 0.922x
prepared/repeated current/V2.14 OptiX: 0.995x and 0.999x
current OptiX vs current Embree on prepared/repeated rows: 105.249x and 63.596x
new current Embree stress regression: 0.891x
```

The result is useful but not a release closure. The next step is a classification decision before more engineering.

## Decision Audit

1. Was it foolish to pause and classify before more POD work?
   No. Continuing POD runs without deciding whether cold single-shot or prepared/repeated behavior is controlling would optimize the wrong metric.

2. If yes, what actions made it foolish?
   Not applicable. The foolish action would be to rerun all-app or retroactively reclassify rows after seeing results.

3. Was there another path?
   Yes. We could immediately tune the cold OptiX path. That is valid only if the strict single-shot row remains the release-control metric.

4. Can we try a different path that solves the real problem?
   Yes. Freeze classification first, then either repair Set-B cold overhead or invest in the Set-A runtime trunk where V3 can earn material gains.

## M26 Proposed Classification

### D1 - LibRTS AABB single-shot count remains Set B/control

Decision: **classify the strict `aabb_index_all_count_only` single-shot row as Set B/control, not Set A.**

Timing-integrity attestation:

- The row classified here is the M22 watch/control row:
  `goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index`.
- History search found prior documents treating **AABB M2.1 native query-handle runner route** as a material Set-A candidate. That is a separate runner-probe packet, not the strict M22 LibRTS single-shot watch row.
- History search found the M22 row carried as a watch row or control/problem row, not as a frozen Set-A release row.
- Therefore D1 is not a demotion of a previously frozen Set-A row. It is the first explicit classification of the M22 watch row under the Set-A/Set-B scorecard.

Rationale:

- It is a lone primitive route, not a multi-phase/residency-rich app workflow.
- The Set-A claim must come from cross-phase RTDL runtime behavior, not from a single primitive row.
- Reclassifying this row as Set A after seeing the result would violate the freeze rule.

Implication:

- The strict `0.922x` result remains a Set-B regression/control-row issue.
- It must be fixed to parity or carried with an accepted user-language explanation.
- Codex recommendation: **fix it if feasible**, because a new runtime should not tax simple single-shot users.

### D2 - Prepared/repeated AABB OptiX is supporting runner evidence, not release Set-A proof

Decision: **prepared/repeated AABB OptiX may be used as runner plumbing and RT hardware sanity evidence, but not as the main V3 Set-A performance proof.**

Rationale:

- It proves the productized runner route is active.
- It proves the hot OptiX path is healthy.
- It does not prove the cross-phase residency/continuation runtime that V3 needs as its main performance source.

Implication:

- Keep the M25 evidence.
- Do not count it as a primary Set-A release win.
- Use it to guard against false "OptiX is slow" conclusions.
- Keep the historical AABB M2.1 runner-probe classification separate. If a future scorecard counts an AABB runner-probe as Set A, it must name that exact pre-frozen row and cannot substitute the M22 LibRTS single-shot watch row after the fact.

### D3 - No all-app run until at least two real Set-A probes have material runtime-sourced gains

Decision: **continue the all-app freeze.**

Rationale:

- M22 already showed the blended all-app result is `1.012x`.
- Without more runtime-sourced Set-A gains, another all-app run will mostly re-confirm parity and burn POD time.

Exit condition to unlock all-app:

```text
>= 2 Set-A probes:
  productized_execution_path == prepared_execution_session_runner
  runtime_executed == True
  focused same-POD V3/V2 material gain >= 1.15x
  preferred focused same-POD V3/V2 material gain >= 1.20x
  no hidden app-specific bypass
  boundary/control rows documented
```

## Work Packages And Resource Estimate

POD cost assumption from user: **about $1 per 4 hours**, i.e. **$0.25/hour**.

| Work package | Purpose | POD needed? | Estimated wall time | Estimated POD time | Cost at $0.25/h | Stop condition |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| M26 classification + 2-AI consensus | Freeze row classification and next work order | No, except Claude local | 0.5-1.0 h | 0 h | $0 | Claude rejects or asks for amended classification |
| M27 LibRTS AABB Set-B triage/repair | First reproduce the Embree 32768 stress regression; then try to bring strict cold single-shot OptiX from `0.922x` to `>=0.950x` | Yes, focused only | 2-4 h | 0.5-1.5 h | $0.13-$0.38 | If Embree repeats below `0.950x`, log separate blocker; if one focused OptiX repair run cannot approach `>=0.950x`, stop and document accepted explanation requirement |
| M28 Set-A trunk selection/freeze | Pick the first true Set-A family and freeze input sizes/metrics before coding | No | 0.5-1.0 h | 0 h | $0 | If family cannot prove cross-phase residency, reject it |
| M29 Step-1 runtime trunk on one Set-A family | Make one residency-rich family execute end to end through the productized runner | Mostly local; POD for focused validation | 4-8 h | 1-2 h | $0.25-$0.50 | If productized path cannot execute without bypass, block and redesign |
| M30 Focused Set-A material probe | Same-POD V2.14/current A/B on that one family | Yes | 1-2 h | 0.5-1.5 h | $0.13-$0.38 | If focused speedup is below `1.15x`, do not count it as a material Set-A win; `1.20x` remains preferred |
| M31-M33 Generalize to two more Set-A families | Prove the trunk is not one-off | Yes, focused only | 8-16 h | 2-4 h | $0.50-$1.00 | If a family is below `1.15x` or wins from route-specific caches/bypasses, it does not count |
| M34 Residency/accounting hardening | Measured phase accounting and no-hot-path host materialization flags | Yes, light validation | 4-8 h | 1-2 h | $0.25-$0.50 | If residency is only metadata assertion, block |
| M35 First all-app paired run | Only after >=2-3 Set-A probes pass | Yes | 2-4 h setup/readout | 4-8 h | $1.00-$2.00 | If Set-A or Set-B gates fail, no release |

## Near-Term POD Recommendation

For the next 12 hours:

- Keep POD available if possible.
- Expected paid POD usage should be **1-3 hours** unless M27/M29 focused validation succeeds and unlocks more probes.
- Expected cost for the near-term push: **about $0.25-$0.75**.
- Do **not** reserve budget for another all-app run yet.

For the full Phoenix V3 path to a serious release-candidate run:

- Optimistic: **2-3 days of focused engineering**, **6-12 POD hours**, about **$1.50-$3.00** POD cost.
- Realistic: **3-5 days**, **10-20 POD hours**, about **$2.50-$5.00** POD cost.
- If Step-1/Step-2 trunk gains fail: stop early after **2-4 POD hours** and reframe V3 as capability/quality, not speed.

These estimates exclude human review latency and assume the POD remains reachable.

## Immediate Next Engineering Order

1. Finish M26 external review and 2-AI consensus.
2. M27: first reproduce/triage the Embree 32768 stress regression. If reproducible below `0.950x`, log it as an independent blocker. Then repair or formally explain the LibRTS AABB Set-B cold single-shot regression.
3. M28/M29: return to the real Phoenix V3 lever: one true Set-A runtime trunk family, preferably fixed-radius self-query -> grouped/component continuation or the already-audited Barnes-Hut fused aggregate-tree path if it can be made runner-owned without bypass.
4. Keep all-app frozen until M29/M30 focused Set-A evidence exists.

## Non-Authorization

This plan does not authorize:

- V3 release.
- Public speedup wording.
- Full all-app rerun.
- Reclassifying rows after results.
- Counting AABB single-shot as Set A.
- V4/external zero-copy/embedding scope.
