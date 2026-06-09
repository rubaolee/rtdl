# Goal4170: Claude Review — Goal4169 RT-DBSCAN Road3D 2M Scale Probe

Verdict: **accept**

Date: 2026-06-09
Reviewer: Claude (Sonnet 4.6), independent read-only review
Commit reviewed: `37805153` — Goal4169 add RTDBSCAN 2M scale probe

---

## Scope

Primary files reviewed:

- `docs/reports/goal4169_rtdbscan_road3d_2m_scale_probe_pod.json`
- `docs/reports/goal4169_rtdbscan_road3d_2m_scale_probe_2026-06-09.md`
- `tests/goal4169_rtdbscan_road3d_2m_scale_probe_test.py`
- `src/rtdsl/current_benchmark_route_decisions.py`

Context files reviewed:

- `docs/reports/goal4168_current_route_decision_after_policy_aware_rtdbscan_2026-06-09.md`
- `docs/reports/goal4165_mixed_predicate_policy_variant_probe_2026-06-09.md`
- `docs/reports/goal4164_rt_dbscan_all_predicate_only_mode_2026-06-09.md`

---

## Q1: Schema distinction between generic component-size and RT-DBSCAN app signature

**Finding: correctly distinguished throughout.**

The pod JSON, the report, and the test all maintain a clean three-way separation:

| Row | Signature shape | `same_signature` in comparisons |
|---|---|---|
| `current_grouped_stream_numba` | `cluster_sizes / core_count / noise_count` | reference |
| `prepared_direct_status_until_stable` | `component_count / component_sizes / contract / point_count` | `false` |
| `predicate_all_true_until_stable` | `cluster_sizes / core_count / noise_count` | `true` |

The report states this distinction explicitly: "The plain prepared direct-status row returns the generic component-size signature schema. It has one component of size 2,097,152, matching the component size meaning of the reference, but it does not include the RT-DBSCAN `cluster_sizes/core_count/noise_count` app signature shape."

The test `test_plain_component_signature_is_fast_but_not_the_app_signature_shape` encodes this as:
- `assertNotEqual(generic["signature"], current["signature"])`
- `assertEqual(generic["signature"]["component_sizes"], [2_097_152])`
- checks that the component size value equals the reference cluster size value without asserting identical schema

The `test_comparison_records_exact_wrapper_match_only` test checks `assertFalse(comparisons["prepared_direct_status_until_stable"]["same_signature"])` and `assertTrue(comparisons["predicate_all_true_until_stable"]["same_signature"])`.

No conflation of the two schema shapes is present in any artifact.

---

## Q2: Bounded claim — all-predicate wrapper matches RT-DBSCAN signature and stays above parity at road3d 2M

**Finding: supported by the measured data.**

The pod records:

- `predicate_all_true_until_stable.reported_elapsed_sec = 20.51367548853159`
- `current_grouped_stream_numba.reported_elapsed_sec = 28.948369339108467`
- Speedup: `1.4111741874483874` — above 1.0, meaning the candidate is faster
- `same_signature: true`
- `all_predicate_fast_path: true`, `all_predicate_fast_path_observed: true`, `all_predicate_fast_path_required: true`
- `border_candidate_updates: 0`
- `direct_status_convergence_proven: true`
- `signatures_stable: true` (repeat=2, warmup=1 protocol)

Road3d was the profile with the weakest margin at 1M (1.396x replay). At 2M it measures 1.411x — a slight uptick, consistent with the stable road-like topology at larger scale. The claim that the route "remains above parity" at road3d 2M is supported.

The test `test_comparison_records_exact_wrapper_match_only` independently verifies `speedup > 1.4`.

One observational note: `point_count = 2,097,152` is exactly 2^21 (a power-of-two allocation), and the road3d dataset produces a single component of all 2,097,152 points with all core, zero noise. That result is consistent with the road3d topology at smaller scales and does not raise a data-integrity concern. The test explicitly checks `core_count == 2_097_152` and `noise_count == 0` indirectly through the signature equality assertion.

---

## Q3: Registry update remains advisory; avoids hidden route, partner, factor, or border-policy selection

**Finding: structurally enforced, not merely documented.**

The `CurrentBenchmarkRouteDecision` dataclass `__post_init__` method raises `ValueError` if any of nine authorization flags is non-False:

```
automatic_partner_selection_authorized
release_authorized
public_speedup_claim_authorized
whole_app_speedup_claim_authorized
broad_rt_core_claim_authorized
true_zero_copy_claim_authorized
paper_reproduction_claim_authorized
amd_performance_claim_authorized
app_specific_native_engine_logic_allowed
```

`user_explicit_choice_required` must remain `True` or construction fails. The `explain_current_benchmark_route` function additionally sets `automatic_partner_selection_authorized: False` on the returned dict independently of the stored row.

The `CURRENT_BENCHMARK_ROUTE_DECISION_STATUS = "internal_route_guidance_not_auto_dispatch"` string makes the advisory nature machine-readable.

The `user_choice_guidance` field for `rt_dbscan` ends: "Do not auto-select the partner, route, factor, or border policy." This explicitly names all four dimensions of hidden selection that have been blocked across the Goal4088-4169 chain.

The version bump from `goal4168.v1` to `goal4169.v1` is the only structural change in this commit to the registry. No new dispatch logic, no automatic selection, no new route promotion.

---

## Q4: No release, public speedup, whole-app, broad RT-core, or route-promotion overclaims

**Finding: clean.**

The report status line is "accepted bounded scale evidence; no route promotion." The boundary section is exhaustive:

> "This report does not authorize automatic route selection, automatic partner selection, automatic factor selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims."

The pod top-level `claim_boundary` object confirms all six authorization flags are `false`. The `benchmark_timing_breakdown.notes` array on both timed rows includes: "This timing packet does not authorize a paper, broad RT-core, or whole-app speedup claim."

The report table column reads "Same RT-DBSCAN signature" not "speedup" or "improvement." The interpretation paragraph says "the all-predicate route remains credible as an explicit user-selected route" — not a default, not a promotion, not a universal claim.

The test `test_report_keeps_boundary_and_interpretation_precise` verifies six specific phrases including "does not solve mixed-predicate rows" and "does not authorize automatic route selection" are present in the report text.

No overclaims found.

---

## Q5: Does this evidence change the next engineering priority?

**Finding: no change to priority. Mixed-predicate border policy and one-shot prepare cost remain the next targets.**

Goal4169 is a scale-extension probe of a narrow, already-existing all-predicate-only mode (established in Goal4164). It answers one question — does the mode stay useful at 2M on road3d — and answers it affirmatively. It does not touch:

- Mixed predicate rows: still blocked, still waiting on an explicit border-assignment policy primitive (Goal4165 showed no grouped-stream switch resolves the gap)
- One-shot prepare cost: still prepare-dominated for the default app route (Goal4109 established this; it has not been revisited)
- Broader profile coverage beyond the current road3d/clustered3d/ngsim_dense scale packet

The registry `next_runtime_action` field states: "next serious runtime work is either one-shot prepare-cost reduction, broader profile coverage beyond the current 65k/131k/262k/524k/1M packet, or a generic border-assignment policy primitive if mixed-predicate component-size distributions must be contractual."

The report itself says: "This does not solve mixed-predicate rows. Goals4165-4168 still stand: mixed predicate component-size contracts require an explicit border-assignment policy."

This evidence is confirmatory, not directionally novel. The engineering priority stack is unchanged.

---

## Summary

Goal4169 is a well-scoped scale probe. All five review questions resolve cleanly:

1. Generic component schema and RT-DBSCAN app signature shape are correctly distinguished in pod, report, and test — no conflation.
2. The bounded claim (all-predicate wrapper matches signature, stays above parity at road3d 2M) is supported by measured data with signature equality confirmed and 1.411x speedup recorded.
3. The registry update is structurally enforced as advisory — construction fails if any authorization flag becomes non-False; no hidden selection path exists.
4. No overclaims present; boundary language is complete and present in both the pod and the report.
5. Engineering priorities are unchanged — mixed-predicate border policy and one-shot prepare cost remain the next targets.

**Verdict: accept**
