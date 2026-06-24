# External Review: Phoenix V3 M69 RTNN Phase/Shape Bridge Audit

Date: 2026-06-23

Reviewer: Claude (external seat)

Status:
`accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release`

Verdict:

```text
accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release
```

## Non-Authorization

This review does not authorize:

- no V3 release
- no all-app benchmark run
- no POD spend
- no paid POD spend
- no focused POD spend
- no runbook execution
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no RT-core speedup claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure

## Review Scope

This review addresses the six questions in the call for review, verifies the
phase arithmetic against the raw evidence JSON, checks the source files for
the bridge claims, confirms the non-authorization set, and assesses the stop
conditions before issuing a verdict.

---

## Q1: Is RTNN bridgeable to the generic `fixed_radius_ranked_summary_3d_prepared_session` runner surface?

**Finding: correct.**

Source inspection confirms the bridge is real and not inferred.

`examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` line 500
calls `rt.run_fixed_radius_ranked_summary_3d_prepared_session()` directly inside
`rtnn_prepared_execution_ranked_summary_payload`. The mode name is
`"prepared_execution_ranked_summary"` (line 535, `"mode": ...`). This mode is
distinct from the legacy front door (`prepared_optix_ranked_summary`, line 400)
which routes through the goal2348 external runner.

`src/rtdsl/prepared_execution.py` at `run_fixed_radius_ranked_summary_3d_prepared_session`
(line 855) accepts explicit `backend` ("optix" or "embree"), `partner`, and
`precision` parameters with no RTNN-specific logic. The distribution support for
the bridge is therefore generic: all three frozen distributions (uniform, clustered,
shell) and both point counts (65536, 262144) are handled by the same helper path.

The source surface checks are confirmed accurate:
- `app_prepared_execution_ranked_summary_mode_exists: true`
- `app_productized_mode_calls_generic_helper: true`
- `prepared_helper_generic_contract_present: true`
- `distribution_bridge_supported: {clustered: true, shell: true, uniform: true}`
- `route_decision_separates_contracts: true`

One constraint noted and correctly disclosed: the productized app mode enforces
full-batch self-queries (`batch_size != point_count` raises ValueError, line
469-470 of the app). This is accurately recorded as
`prepared_execution_requires_full_batch_self_queries: true`. All 14 frozen
RTNN all-app rows are self-query shapes, so this constraint does not block the
bridge now. **The M70 protocol must carry this constraint explicitly** and must
not propose non-self-query batch shapes without a separate code path review.

**Q1 accepted.**

---

## Q2: Is the phase attribution correct and sufficiently honest?

**Finding: numerically verified, disclosure is adequate.**

All figures were cross-checked against
`docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/summary.json`.

Phase arithmetic:

| Metric | Raw evidence | Report | Match |
| --- | ---: | ---: | --- |
| Legacy runner wall | 3.208734s | — | ✓ |
| Runner runner wall | 2.341841s | — | ✓ |
| Total delta | 0.866893s | 0.866893s | ✓ |
| Legacy input_load + input_pack | 1.500658 + 0.494792 = 1.995450s | 1.995450s | ✓ |
| Runner input_load_pack | 1.715503s | 1.715503s | ✓ |
| Input load/pack delta | 0.279946s | 0.279946s | ✓ |
| Input load/pack share | 0.279946 / 0.866893 = 0.3229 | 0.323 | ✓ |
| Legacy after input pack | 3.208734 − 1.995450 = 1.213284s | 1.213284s | ✓ |
| Runner after input pack | 2.341841 − 1.715503 = 0.626338s | 0.626317s | ✓ (rounding) |
| Runner-after-pack delta | 0.586967s | 0.586967s | ✓ |
| Runner-after-pack share | 0.586967 / 0.866893 = 0.6771 | 0.677 | ✓ |
| Legacy execution_prepare | 0.409430s | 0.409430s | ✓ |
| Runner execution_prepare | 0.052025s | 0.052025s | ✓ |
| execution_prepare delta | 0.357405s | 0.357405s | ✓ |
| Hot-query speedup | 0.010689 / 0.010810 = 0.98878x | 0.988781x | ✓ |

The 0.988781x hot-query result (runner is **marginally slower** on hot queries
than legacy) is correctly disclosed. The report does not convert this to a
positive claim. The phase decomposition is explicitly described as split across
input packing, prepare/session reuse, and runner-after-pack — not solely from
any single phase.

Two transparency notes that do not block acceptance but should carry forward:

1. **Distribution scope of the repeat50 run.** The phase attribution was
   measured on the uniform distribution only (seed 20260622, 1,048,576 points).
   The all-app scorecard includes clustered and shell shapes, several of which
   sit well below 1.0x (e.g., `rtnn_embree_clustered_262144_ranked_summary`
   at 0.9457x). The runner-wall phase split may differ across distributions
   because input packing cost scales with data locality. The M70 protocol must
   not present the uniform-distribution phase attribution as representative of
   clustered or shell performance. Per-distribution phase bounds belong in the
   focused protocol, not in the bridge audit.

2. **Input pack comparison heterogeneity.** The legacy path separates
   `input_load_sec` and `input_pack_sec` as distinct timing fields; the runner
   reports them as a single `input_load_pack_sec`. The combined comparison is
   reasonable and correctly applied, but the sources are measured at different
   granularities. This is acceptable for a bridge audit and does not need
   correction here.

**Q2 accepted.**

---

## Q3: Does M69 correctly identify the front door / productized runner distinction?

**Finding: correct.**

Source confirms two distinct paths:

**Legacy front door** (`prepared_optix_ranked_summary`, app line 400):
routes through `goal2348_rtnn_v2_2_external_runner.run_rtdl_batched_3d_neighbors`
with `result_mode="ranked-summary-aggregate-prepared-query-batch-float32"`.
The mode string `"prepared_optix_ranked_summary"` appears in the evidence under
`legacy_app_front_door_prepared_optix.mode`. The scale profile and current
benchmark front door both use this path, confirmed by
`scale_profile_uses_prepared_optix_ranked_summary: true` and
`front_door_uses_prepared_optix_ranked_summary: true`.

**Productized runner mode** (`prepared_execution_ranked_summary`, app line 535):
calls `rt.run_fixed_radius_ranked_summary_3d_prepared_session()` directly,
routes through `PreparedExecutionSessionTask` / `_execute_prepared_execution_session`
in `prepared_execution.py`, and records
`productized_execution_path: "prepared_execution_session_runner"`.

The distinction is real, correctly described, and supported by the evidence.
The checks `front_door_currently_legacy_prepared_optix: true` and
`productized_runner_mode_exists: true` are accurate.

**Q3 accepted.**

---

## Q4: Is the M70 recommendation correct?

**Finding: appropriate and correctly scoped.**

M68 authorized only `local_rtnn_ranked_summary_phase_shape_bridge_audit`. M69
has not been granted authority to propose a runbook, POD, or all-app run. The
correct incremental step is a reviewed focused protocol with no execution.

The all-app scorecard state supports this conservatism: 13 of 14 rows remain
below 1.05x, 6 of 7 shape groups remain below 1.05x. There is no app-win
demonstrated at the all-app level. A focused protocol in M70 is the right
place to:
- Name the exact frozen RTNN shapes to be probed.
- Define per-distribution bounds for phase attribution.
- Set the incumbent comparison contract for each shape.
- Preserve all existing non-authorization boundaries.
- Record the self-query constraint.

If external review rejects M69 (this review accepts it), the fallback to
Triangle or RTDBSCAN reserve candidates is correctly documented in the
goal-level decision audit.

**Q4 accepted.**

---

## Q5: Are the stop conditions sufficient?

**Finding: substantially sufficient; one gap noted for M70 carry-forward.**

The five listed stop conditions are evaluated:

1. **Stop if external review rejects the all-app shape bridge.** Correct and
   necessary.
2. **Stop if the bridge requires app-specific RTNN native logic.** Correct. The
   app has RTNN-specific graph partner bridge modes, but the productized runner
   mode routes only through the generic helper. The generic helper has no RTNN
   symbol, no ANN index, and no native RTNN-specific logic. This stop condition
   is correctly gated.
3. **Stop if the positive signal is only repeat50 amortization with no shape
   bridge.** Correct. The runner-wall result is repeat50 focused evidence; the
   stop condition prevents that alone from authorizing a runbook.
4. **Stop if phase attribution shows only input-loading/packing consolidation
   and no runner-after-pack or prepare/session contribution.** Correct. The
   67.7% runner-after-pack share clears this condition. The
   `phase_attribution_runner_after_pack_positive: true` and
   `phase_attribution_not_input_pack_only: true` checks are accurate.
5. **Stop if exact aggregate, graph partner bridge, and productized prepared-session
   contracts are mixed into one public claim.** Correct. The app contains at
   least four distinct contract types (ranked_summary aggregate, raw rows, graph
   partner bridge, typed stream). This stop condition is necessary and correctly
   stated.

**Gap not listed as a stop condition but noted for M70:**

The repeat50 evidence covers uniform distribution only. The stop conditions do
not include: "Stop if the focused protocol claims per-distribution phase bounds
derived from a single-distribution runner-wall measurement." The M70 protocol
must not extrapolate the uniform-distribution phase split to clustered or shell
shapes without per-distribution evidence. This is not a blocker for bridge
acceptance (phase attribution at the bridge stage is about runner-surface
compatibility, not per-shape speedup claims), but it must be stated explicitly
as a M70 requirement.

**Q5 accepted with carry-forward note.**

---

## Q6: Are the non-authorization boundaries complete?

**Finding: complete.**

The JSON `non_authorization` block contains 14 fields, all false. Cross-checked
against the call-for-review non-authorization list:

| Required item | JSON field | Value |
| --- | --- | --- |
| no V3 release | `release_authorized` | false ✓ |
| no all-app benchmark run | `all_app_run_authorized` | false ✓ |
| no POD spend | `pod_authorized` | false ✓ |
| no paid POD spend | `paid_pod_spend_authorized` | false ✓ |
| no focused POD spend | `focused_pod_spend_authorized` | false ✓ |
| no runbook execution | `runbook_authorized` | false ✓ |
| no public speedup wording | `public_speedup_claim_authorized` | false ✓ |
| no broad V3-over-V2 claim | `broad_v3_over_v2_claim_authorized` | false ✓ |
| no whole-app speedup claim | `whole_app_speedup_claim_authorized` | false ✓ |
| no paper reproduction claim | `paper_reproduction_claim_authorized` | false ✓ |
| no RT-core speedup claim | `rt_core_speedup_claim_authorized` | false ✓ |
| no automatic partner selection | `automatic_partner_selection_authorized` | false ✓ |
| no route-specific RTNN app tuning | `route_specific_rtnn_app_tuning_authorized` | false ✓ |
| no watch-row closure | `watch_row_closure_authorized` | false ✓ |

All 14 items are present and false. No item is missing or set incorrectly. The
non-authorization set is complete.

**Q6 accepted.**

---

## Summary of Findings

| Question | Finding | Status |
| --- | --- | --- |
| Q1: Bridge to generic runner surface | Bridge is real, app already calls helper, distributions supported | Accept |
| Q2: Phase attribution honesty | Arithmetic verified, 0.988781x hot-query boundary disclosed, uniform-only scope noted | Accept with note |
| Q3: Front door vs productized runner | Both identified correctly from source | Accept |
| Q4: M70 recommendation | Appropriate incremental step | Accept |
| Q5: Stop conditions | Substantially sufficient; distribution-scope gap for M70 | Accept with carry-forward |
| Q6: Non-authorization completeness | All 14 items present and false | Accept |

No blocking issues. No local fix required before the bridge decision.

## Carry-Forward Requirements for M70

M70 must carry the following from this review:

1. The repeat50 evidence is uniform-distribution only. Per-distribution phase
   attribution bounds are required in the focused protocol before any runbook
   references a clustered or shell shape.
2. The `prepared_execution_ranked_summary` mode requires full-batch self-queries.
   The focused protocol must name this constraint and must not propose non-self-
   query shapes without a separate code path review.
3. The M70 protocol must name exact frozen RTNN shapes and must identify the
   same-contract incumbent for each shape.
4. The 0.988781x hot-query boundary must be preserved in all M70 protocol
   framing. The runner-wall improvement is not a hot-query speedup claim.
5. All non-authorization boundaries listed in this review carry forward
   unchanged. M70 protocol drafting does not authorize execution, POD, release,
   or any public claim.

## Verdict

```text
accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release
```

M69 is accepted. RTNN is bridgeable to the generic
`fixed_radius_ranked_summary_3d_prepared_session` runner surface. The phase
attribution is correct and honest. The non-authorization set is complete. M70
may draft a reviewed focused protocol with no execution.
