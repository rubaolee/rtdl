I have everything I need. Here is the written review.

---

## Second AI Review — Phoenix V3 M25 LibRTS AABB OptiX Runner Watch Row
**Date:** 2026-06-23  
**Reviewed by:** Claude (second reviewer)  
**Verdict:** `partial_not_closed`

---

### Summary

M25 produced genuine, well-structured evidence about the M22 watch row. It confirmed that current is running the productized Phoenix prepared-execution/session runner, demonstrated that the prepared/warm OptiX path is at parity with V2.14, and added a meaningful regression test that guards runner contract bypass. None of that closes the watch row. The strict single-shot no-warmup result is **0.922x**, 28 basis points below the 0.950x threshold. The blocker is not closed.

---

### Six Review Questions

**Q1. Does M25 close the M22 LibRTS AABB OptiX watch row, or is it only partial evidence?**

Partial evidence only. The M22 watch row measured `goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix` at 0.803x. M25 re-measures the same scenario on the same POD at 0.922x. That is an improvement but it remains below the 0.950x threshold. A watch row is not closed because it moved in the right direction; it is closed when the threshold is met or the scorecard classification is formally revised. Neither happened here.

The focused run also does not substitute for an all-app rerun. M25 ran three scenarios on one POD with no all-app coverage. It cannot redeem the watch row in the release scorecard.

**Q2. Is 0.922x on the strict single-shot no-warmup row acceptable under the existing 0.950x watch threshold?**

No. The threshold is 0.950x. The measured result is 0.922x. Current OptiX is measurably slower than V2.14 OptiX on a cold single-shot 2048-box run: 0.29973s vs 0.27646s, a delta of ~23ms. The JSON confirms this is a true single-shot measurement (`measured_repeat_count: 1`, `warmup: 0`, `repeated_prepared_session_execution: false`). There is no ambiguity in the number.

The fact that the gap improved from 0.803x (M22) to 0.922x (M25) is meaningful progress and should be on the record, but the threshold stands at 0.950x and this result is below it. Saying the watch row is acceptable at 0.922x would require explicitly revising the threshold, which this packet does not do.

**Q3. Does the repeat/prepared evidence (0.995x, 0.999x, 63x–105x OptiX-vs-Embree) justify reclassifying this row as a prepared/repeated Set-A route with a cold single-shot control?**

The evidence provides the factual basis for a reclassification argument but does not constitute the reclassification itself.

The prepared/warm path results are genuinely healthy:
- `repeat50` OptiX: 0.995x vs V2.14 (essentially parity)  
- `stress_32768` OptiX: 0.999x vs V2.14 (essentially parity)  
- Hot OptiX vs current Embree: 105x and 63x faster respectively

The structural case is clear: the single-shot result measures cold-path prepare overhead, not steady-state OptiX kernel performance. The current Phoenix prepared runner has a prepare phase of 0.2699s vs V2.14's 0.2522s, a ~17.7ms additional setup cost that disappears entirely when the session is retained across repeats. This is worth understanding and the M25 packet explains it well.

However, "the evidence justifies reclassification" and "reclassification is authorized" are not the same thing. The M22 watch row was written as a single-shot cold scenario. Reclassifying it as a Set-A prepared/repeated row is a scorecard decision that must be made explicitly by the responsible engineering owner with a documented boundary. M25 does not contain that decision. Until it does, the cold/single-shot row remains the controlling metric and 0.922x remains below threshold.

**Q4. Is the new OptiX runner contract test sufficient to prevent regression where current silently bypasses the productized runner?**

Yes, for the stated purpose. `test_optix_aabb_count_route_uses_productized_prepared_query_set_runner` correctly patches `rtdsl.run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session` at the import-time binding and verifies it is called exactly once with `operation="all"`, `partner="none"`, `device="cuda:0"`, `warmup_count=1`, `measured_repeat_count=3`, `retain_repeat_outputs=True`. If the production route is changed to bypass this function, the mock will not trigger, `len(calls)` will be 0, and the test will fail. That is a valid regression guard.

The test also correctly asserts `release_authorized=False`, `public_speedup_claim_authorized=False`, and `broad_v3_faster_than_v2_claim_authorized=False` in the metadata, which prevents the runner contract from being used to bootstrap authorization claims.

One note: the test uses `_FakeRunnerResult` returning hardcoded values, so it tests contract wiring, not correctness. That is appropriate for a unit-level regression guard. The correctness evidence comes from the 42-test POD run and the field JSON with `matches_cpu_reference: true`.

**Q5. Should the next action be cold/hot split tuning, Embree 32768 regression, scorecard reclassification, or move to next Set-A family?**

The next action should be a **scorecard classification decision**, not an engineering step, and it should happen before the team picks between the other three options. The reason: the correct engineering path depends entirely on whether single-shot cold OptiX is a controlling V3 metric or a documented control row.

- If the classification decision is "single-shot cold OptiX is controlling": the next engineering step is cold first-query tuning to close the 0.922x → 0.950x gap on the existing watch row.
- If the classification decision is "prepared/repeated Set-A is the V3 user path and single-shot is a documented control": the reclassification must be written into the scorecard, the cold row must be retained as an explicit boundary-with-explanation, and then the team can move to the next Set-A family.

In either case, the Embree large stress regression (0.891x on `stress_32768x1024_r20w5`) is a **new open blocker revealed by M25** that was not in the original M22 watch row. Current Embree took 1.0055s vs V2.14's 0.8958s on the 32768-box run — 12.2% slower. This finding must be logged and addressed separately from the OptiX watch row, regardless of which OptiX path is chosen.

**Q6. Is any public speedup/release wording authorized by this packet?**

No. Nothing in this packet authorizes any of the following:

- V3 release
- Full all-app rerun
- Public speedup wording
- Broad "V3 is faster than V2.x" wording
- Hiding or omitting the strict single-shot 0.922x result
- V4/external zero-copy/embedding claims

The evidence JSONs themselves independently record `release_authorized: false`, `public_speedup_claim_authorized: false`, and `broad_v3_faster_than_v2_claim_authorized: false` at every layer (run, runner, session, report). The packet is internally consistent on this.

---

### Additional Findings Not in the Call-For-Review

**New blocker revealed by M25:** The `stress_32768x1024_r20w5` Embree row shows `current/V2 Embree = 0.891x` (current: 1.0055s, V2.14: 0.8958s). This is a distinct regression from the original OptiX watch row and was not a known open blocker before M25. It should be formally logged.

**Runner path divergence between current and V2.14:** V2.14 uses `primitive_contract: "generic_prepared_aabb_index_query_2d"` with `explicit_reuse_helper: "get_or_prepare_explicit_session"`. Current uses `"generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count"` with the Phoenix productized runner. The comparison is structurally valid (same fixture, same POD, same backend), but the two paths are architecturally different. The 0.922x cold-path gap is partly attributable to the new runner's additional prepare phase overhead (~17.7ms extra). This is useful context for the scorecard classification decision but does not change the verdict.

**Progress log is clean:** All 12 runs completed in sequence on 2026-06-23 between 12:49:46Z and 12:51:05Z with no stderr output. The environment hashes are recorded. Evidence is properly linked.

---

### Open Blockers After M25

| # | Blocker | Status | Threshold |
|---|---------|--------|-----------|
| 1 | Strict OptiX watch row (M22): single-shot cold `0.922x` | **Not closed** | 0.950x |
| 2 | Embree large stress `stress_32768x1024_r20w5`: `0.891x` | **New, unlogged** | — |
| 3 | Scorecard classification of single-shot vs prepared/repeated | **Pending decision** | — |

---

### Verdict

**`partial_not_closed`**

M25 is competent, honest work. The runner contract is confirmed. The cold/hot gap is explained. The test is a real regression guard. But the M22 watch row threshold is 0.950x and the strict measured result is 0.922x. That gap does not close itself by being understood. The watch row remains open. M25 also surfaces a new Embree regression that was not previously on record. The team has more work ahead, not less, after this milestone.
