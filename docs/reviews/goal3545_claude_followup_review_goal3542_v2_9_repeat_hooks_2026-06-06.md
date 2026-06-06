# Goal3545 - Claude Follow-up Review: Goal3542 v2.9 Repeat/Resident Hook Coverage

Reviewer: Claude (follow-up after Goal3543 patch)
Date: 2026-06-06
Verdict: **accept-with-boundary**

---

## Purpose

This is a targeted follow-up to Goal3543 (the initial Claude review of Goal3542). Goal3543 raised four concerns; this review verifies whether each is now closed after the patch round.

Files inspected:

- `docs/reports/goal3542_v2_9_repeat_resident_hook_coverage_2026-06-06.md`
- `docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3542_V2_9_REPEAT_HOOKS_2026-06-06.md`
- `docs/handoff/HANDOFF_POD_V2_9_REPEAT_HOOK_10S_RERUN_2026-06-06.md`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `tests/goal3542_v2_9_repeat_resident_hook_coverage_test.py`

---

## Concern 1: RayJoin raw-view repeat count-stability

**Status: Closed.**

The `_phase_repeat_time` helper now accepts a `stability_value` callable (rayjoin app, lines 262–291). When called on any raw-view path — `run_raw_once` for `overlay_seed` and `lsi`, and `run_positive_hits_once` for `pip` — the caller passes `stability_value=lambda value: int(value[0])`, where `value[0]` is the row count from the `(row_count, rows)` tuple. Each inner `run_*_once` closure opens a view, reads from it, and closes it in a `finally` block before returning. The stability check then collects the row-count identity across all measured iterations and raises `RuntimeError(f"{label} repeat changed result identity")` if any divergence is detected. The test in `goal3542_v2_9_repeat_resident_hook_coverage_test.py` (lines 69–70) asserts both `"stability_value"` and `"repeat changed result identity"` appear in the RayJoin source.

The concern was specifically about the raw-view path; the count-only path does not use `stability_value`, which is acceptable because an integer count returned from a resident prepared handle over identical inputs carries implicit stability — there is no mutable view object to leak.

---

## Concern 2: LibRTS summed-median naming

**Status: Closed without breaking compatibility.**

Both `run_optix_aabb_counts` and `run_embree_aabb_counts` now emit two fields in `run_phases`:

```python
"query_median_sec": float(sum(query_sec.values())),      # compatible alias
"query_summed_median_sec": float(sum(query_sec.values())), # explicit name
```

`query_summed_median_sec` is the authoritative label communicating that the all-operation metric is a sum of per-operation medians. `query_median_sec` is kept as a compatible alias so that the Goal2626 registry's `primary_metric_path=("run_phases", "query_median_sec")` continues to resolve without a registry edit. The registry test (line 58) confirms the registry still references the compatible path. The report (table row for `librts_optix_aabb_index`) explicitly documents the semantics: "summed median query time across requested AABB operations (`query_summed_median_sec`, kept compatible as `query_median_sec`)." The test (line 79) asserts `query_summed_median_sec` is present in the LibRTS source.

One residual nuance: when the planner runs a single operation rather than all three, `query_median_sec == query_summed_median_sec` and both are a true per-operation median, so the label is not misleading in that case. The naming only needs the explicit `query_summed_median_sec` clarification in the multi-operation all-ops case, which is what the registry exercises. No further action required.

---

## Concern 3: Report clearly distinguishes current-tree coverage from v2.3 historical evidence

**Status: Closed.**

The report enforces this distinction in at least four places:

1. The opening scope note (lines 6–7): "the hooks are implemented in the current tree. An authoritative v2.3-vs-current timing rerun still needs a same-contract v2.3 evidence checkout."
2. The planner result section (lines 35–36): "This is a measurement-readiness result only. It does not replace the required A5000/pod rerun... It also does not by itself prove that the historical v2.3 evidence checkout has the same repeat controls."
3. The report's final paragraph (lines 60–63): requires a v2.3 evidence checkout that either contains the same measurement-only repeat hooks or is wrapped by a documented same-contract adapter "that changes timing methodology but not v2.3 implementation semantics."
4. The HANDOFF_POD file (preconditions, lines 6–7 and the evidence command comment, lines 53–55) repeats the boundary and flags the `--v23-root` placeholder as requiring a real historical checkout for the authoritative comparison.

The test (lines 29–30) mechanically enforces that both `"same-contract v2.3 evidence checkout"` and `"current tree for both lanes"` remain in the report text. The HANDOFF_EXTERNAL_REVIEW file relays the same boundary in its context section. There is no language in any of these documents that conflates the dry-run result with actual historical v2.3 timing evidence.

---

## Concern 4: No release or speedup claims authorized

**Status: Closed.**

The report's Claim Boundary section (lines 54–63) explicitly lists what Goal3542 does not authorize: v2.9 release, public speedup claims, broad RT-core acceleration claims, whole-app speedup claims, true zero-copy claims, and paper reproduction claims. The test (line 21) asserts `"does not authorize"` appears in the report.

All payload `claim_boundary` dicts in the RayJoin app maintain `False` values for `release_authorized`, `public_speedup_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`, `whole_app_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, and `true_zero_copy_claim_authorized`. The LibRTS app carries the module-level `CLAIM_BOUNDARY` constant that explicitly states "does not authorize public speedup wording" and marks `paper_reproduction: False`, `authors_code_comparison: False` in all payloads.

---

## Remaining open boundary (not a concern about this goal)

The one thing Goal3542 cannot close by itself — and does not claim to — is that the historical v2.3 checkout has the same repeat hooks. That precondition must be verified before the pod rerun (Goal3543 pod step, now documented in HANDOFF_POD). Until that checkout is confirmed and the 10-second steady-state packet actually runs with the new protocol, this milestone is correctly classified as measurement-readiness, not timing evidence.

---

## Overall Assessment

All four concerns raised in Goal3543 are resolved:

| Concern | Status |
| --- | --- |
| RayJoin raw-view count-stability check | Closed |
| LibRTS summed-median naming without breaking compatibility | Closed |
| Report distinguishes current-tree from v2.3 historical evidence | Closed |
| No release/speedup claims authorized | Closed |

The implementation is clean: view lifecycle is correct, stability checks are in the right layer, the compatible alias approach for LibRTS is the right tradeoff, and the claim boundary is tight and test-enforced. The next required step — the pod rerun with an authoritative same-contract v2.3 evidence checkout — is clearly documented in HANDOFF_POD and not pre-empted by anything here.

**Verdict: accept-with-boundary**

The boundary is: this goal is measurement-readiness only. No performance positioning, release authorization, or public speedup language may be derived from the dry-run planner output until the HANDOFF_POD rerun completes with a verified same-contract v2.3 checkout and passes external review.
