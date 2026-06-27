# V4 Gemini Review Debt - Full-Coverage Packet For Antigravity Review

Date: 2026-06-27

Status: `gemini_review_debt_open__antigravity_review_requested__not_release_authorization`

Reviewer requested: Antigravity, acting as an external reviewer for the review
seat that would otherwise have gone to Gemini.

## 0. Why This File Exists

Gemini CLI review is currently not available in this project workflow because
the user reported that Google's CLI policy changed and instructed the main
agent not to keep retrying Gemini until a solution is found. Repeatedly probing
Gemini would be process churn, not engineering progress.

This file therefore consolidates the open Gemini-style review debt into one
full-coverage packet and asks Antigravity to review it as the currently
available external reviewer.

This file is deliberately broad. It covers:

- the current V4.0 release candidate state;
- the complete V2.14 / V3.0.2 / V4.0 10-app RT-core matrix;
- the current user-facing V4 programming model;
- the RT-BarnesHut paper-reproduction delta;
- RayJoin benchmark-vs-paper-reproduction classification;
- historical review debts that appear superseded;
- still-open review debts that should block a public tag or specific wording;
- the exact verdict labels requested from Antigravity.

## 1. One-Sentence Current V4 Status

RTDL V4.0 is a Python eDSL/operator-pushdown release candidate and V2/V3
superset with a complete NVIDIA RT-core 10-app V2.14/V3.0.2/V4.0 matrix,
bounded material wins, broad parity/control elsewhere, additional measured
operator/workflow surfaces, and open external review debt before any public
tag.

Current status source:

- `docs/current_v4_status.md`

Current status label:

```text
complete_rt_core_app_matrix__bounded_material_wins__final_review_evidence_prepared
```

## 2. Core Evidence Package To Review

Antigravity should read these first.

| Purpose | Path |
| --- | --- |
| Current V4 status | `docs/current_v4_status.md` |
| App-level benchmark summary | `docs/app_level_benchmark_summary.md` |
| Final 10-app matrix readout | `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md` |
| Final release packet after Goal4756 | `future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md` |
| Final evidence manifest | `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md` |
| Barnes-Hut author phase accounting | `future/v4/v4_goal4769_rt_barneshut_author_phase_accounting_2026-06-26.md` |
| Barnes-Hut release packet delta | `future/v4/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.md` |
| Full V4 local gate after Barnes-Hut delta | `future/v4/v4_goal4771_full_v4_gate_after_barnes_hut_delta_2026-06-26.md` |
| RT-BarnesHut four-way fair compare | `future/v4/v4_goal4772_rt_barneshut_four_way_fair_compare_2026-06-26.md` |
| RayJoin line classification | `future/v4/v4_rayjoin_benchmark_vs_paper_reproduction_classification_2026-06-27.md` |
| Closure conversation summary | `future/v4/v4_closure_key_conversation_summary_2026-06-27.md` |
| Refresh/runbook with current facts | `future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md` |

Machine/evidence paths:

| Evidence | Path |
| --- | --- |
| Complete 30-row matrix directory | `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/` |
| Matrix summary JSON | `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/summary.json` |
| Matrix analysis JSON | `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json` |
| Final review manifest JSON | `future/v4/evidence/v4_goal4759_final_review_evidence_manifest_2026-06-26.json` |
| Goal4771 full local gate log | `future/v4/evidence/v4_goal4771_full_v4_unittest_discover_after_goal4770_2026-06-26.log` |
| RT-BarnesHut evidence directory | `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/` |
| RT-BarnesHut four-way JSON | `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4772_four_way_fair_compare_pod_2026-06-26.json` |

## 3. V4.0 Release Candidate Claim Under Review

Allowed candidate claim:

```text
RTDL V4.0 is a Python eDSL/operator-pushdown release candidate and V2/V3
superset. On the current NVIDIA RTX A5000 RT-core 10-app matrix, every promoted
benchmark app has V2.14, V3.0.2, and V4.0 rows. V4.0 has two material hot-path
candidate wins over V2.14 and parity/control elsewhere. Separate V4 operator
surfaces and the constrained Numba custom predicate early-exit workflow show
additional bounded V4 value.
```

This is the claim Antigravity should test. If this wording is too strong,
please say exactly which phrase must be changed.

## 4. Current 10-App RT-Core Matrix

Goal4756 completed the serious NVIDIA RT-core POD matrix:

- apps: `10/10`;
- version rows: `30/30`;
- every app has V2.14, V3.0.2, and V4.0 rows;
- all rows returned success and parseable JSON;
- `n/a` rows: none;
- primary denominator: NVIDIA OptiX/RT-core only;
- Embree primary denominator: false;
- hot-path regressions in the Goal4756 table: `0`;
- material hot-path candidates over V2.14: `triangle_counting`, `barnes_hut`;
- hot-path geomean V4/V2.14: `2.10069x`, not authorized as a headline.

Current table:

| App | V4/V2.14 hot | V4/V3.0.2 hot | Current release reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `0.998x` | `0.993x` | Parity/control. |
| RayDB-style | `1.113x` | `1.111x` | Modest hot gain; not broad headline evidence. |
| Triangle counting | `4.360x` | `1.021x` | Material hot-path candidate. |
| LibRTS spatial index | `0.999x` | `1.002x` | Parity/control. |
| Hausdorff XHD threshold route | `1.032x` | `0.983x` | Same-primitive threshold parity/control. |
| Robot collision | `1.020x` | `1.000x` | Parity/control; inherited OptiX primitive remains usable in V4. |
| Contact manifold | `1.116x` | `1.477x` | Parity/control/modest subpipeline gain. |
| RTNN | `1.029x` | `1.024x` | Parity/control. |
| Spatial RayJoin shape-pair | `1.000x` | `1.004x` | Serious generated-input parity/control. |
| Barnes-Hut aggregate frontier | `286.142x` | `0.993x` | Material V3/V4-over-V2.14 candidate; not a new V4-over-V3 speed claim. |

Reviewer questions:

1. Is this complete enough as the public V4.0 10-app matrix?
2. Is it correct that the geomean must not be headlined because Barnes-Hut and
   Triangle dominate it?
3. Does the table preserve fair denominators and avoid Embree-as-primary
   claims?
4. Are any rows still too small, toy-like, or ambiguous for public release?
5. If a row needs a rerun, identify the exact app, route, denominator, and data
   size.

## 5. User-Facing V4 Programming Model Under Review

The intended public model is:

```python
import rtdsl.v4 as rtdl_v4
```

User-facing interpretation:

| Version | User-facing meaning |
| --- | --- |
| V2.14 | Historical/current compatibility layer containing useful RT-core primitives and benchmark routes. |
| V3.0.2 | Compatibility layer containing selected residency/continuation improvements that V4 preserves. |
| V4.0 | Current clean Python eDSL/operator-pushdown front door and V2/V3 superset. Users should learn V4 first. |

Important user-facing principle:

```text
Users should not have to know whether a good route originated in V2.14, V3, or
V4. V4 should expose the current best supported route, while the history stays
in evidence/history docs.
```

Reviewer questions:

1. Does the current documentation make V4 look like the one clean current user
   surface?
2. Does it still expose too much internal history to ordinary users?
3. Are V2/V3 compatibility routes correctly treated as part of V4 instead of
   being excluded from V4?
4. Is the operator-discovery story sufficient, or does V4 still force users to
   guess long low-level function names?

## 6. Operator/Workflow Surfaces Under Review

The current measured V4 operator/workflow surface count is `10`.

Surfaces listed in `docs/current_v4_status.md` include:

- fixed-radius count-threshold;
- closest-hit grouped argmin;
- ray/triangle any-hit flags;
- primitive grouped-i64 reduction;
- point-group nearest witness;
- ray/triangle any-hit weighted sum;
- fixed-radius graph component union;
- AABB all-ops count;
- aggregate-frontier device columns;
- constrained Numba Custom predicate early-exit.

Important boundary:

- These surfaces have explicit denominators and partner scopes.
- They do not authorize whole-application speedup claims.
- They do support the V4 programming-model claim that RTDL has a cleaner
  operator-pushdown front door than V2.14.

Reviewer questions:

1. Are the operator/workflow surfaces documented with enough denominator,
   partner, scale, and claim-boundary information?
2. Is the custom predicate early-exit workflow correctly bounded as a V4-specific
   workflow win rather than arbitrary OptiX callback support?
3. Is Tier-3 callback/PTX support still correctly excluded from V4.0 public
   support?

## 7. RT-BarnesHut Paper-Reproduction Delta Under Review

There are two Barnes-Hut lines and they must not be merged silently:

| Line | Current meaning |
| --- | --- |
| Traditional benchmark Barnes-Hut | One of the 10 benchmark apps. Goal4756 aggregate-frontier row: V4/V2.14 `286.142x`, V4/V3 `0.993x`. |
| RT-BarnesHut paper-reproduction app | Separate author-semantics route. V4 has a checksum-valid native RT-core route at 10M and Author-vs-V4 timing evidence. |

Goal4772 result:

| Row | Same author-semantics route? | Timing ratio allowed? | Result |
| --- | --- | --- | --- |
| Author program | Yes | Reference denominator | Full program `10.4391s`; RT-force `1.12905s`; sort `6.87096s`. |
| RTDL V2.14 | No | No | Explicit route absence for the Goal4760 contract. |
| RTDL V3.0.2 | No | No | Explicit route absence for the Goal4760 contract. |
| RTDL V4.0 | Yes | Yes, against author | Checksum passes; internal program `7.513309154s`; RT-force `0.886653679s`; sort `6.16351s`. |

Valid Author-vs-V4 ratios under the same 10M Treelogy input and
author-semantics contract:

| Comparison | Author seconds | V4 seconds | Ratio |
| --- | ---: | ---: | ---: |
| Full internal program | `10.4391` | `7.513309154` | `1.3894144092875964x` |
| RT-force phase | `1.12905` | `0.886653679` | `1.27338331384739x` |
| Sort phase | `6.87096` | `6.16351` | `1.1147803767658364x` |
| Author sort+tree vs V4 preprocessing | `8.58458` | `6.503060236` | `1.3200831129438122x` |

Current blocked wording:

- public RT-BarnesHut paper-reproduction claim;
- public V2/V3/V4 RT-BarnesHut speed table;
- no-copy or device-resident tree-build claim;
- broad V4 speedup wording.

Allowed internal/review wording:

```text
V4 has a same-semantics native RT-core RT-BarnesHut route that V2.14 and V3.0.2
do not expose. On the same 10M Treelogy input, V4 passes the author checksum and
is about 1.389x faster than the authors' binary on internal program time in the
POD run.
```

Reviewer questions:

1. Is the Goal4772 fairness boundary correct?
2. Is it correct to report V2.14/V3.0.2 as explicit route absence rather than
   timing ratios under the author-semantics contract?
3. Is the Author-vs-V4 timing ratio valid given the exposed author phase table?
4. Is custom-primitive control geometry acceptable for a paper-reproduction
   claim, or must literal author triangle geometry be implemented first?
5. Should public V4.0 mention RT-BarnesHut only as a supplemental engineering
   result, not as public paper reproduction?

## 8. RayJoin Benchmark vs Paper-Reproduction Classification Under Review

RayJoin belongs to two lines, but not through one single app surface:

| Surface | Line | Classification |
| --- | --- | --- |
| `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Benchmark apps | Benchmark app only; it blocks full paper-reproduction wording. |
| `src/rtdsl/rayjoin_paper_suite.py` plus `scripts/rayjoin_paper_reproduction_suite.py` | Paper-reproduction apps | Separate paper-reproduction line, historically v2.x-era. |
| V4 current 10-app matrix `spatial_rayjoin` row | Benchmark apps | Benchmark/control row only, generated grid64 shape-pair input. |

Current conclusion:

```text
RayJoin as a project family: both benchmark and paper-reproduction work.
The current V4 Spatial RayJoin benchmark row: benchmark line only.
The RayJoin paper-reproduction app: separate v2.x/V2.14-era suite, not the
current V4 benchmark row.
```

Reviewer questions:

1. Is this split correct?
2. Does the public V4.0 surface avoid implying that the V4 Spatial RayJoin row
   is the RayJoin paper-reproduction app?
3. If RayJoin paper reproduction is to become a V4 paper-reproduction app, what
   exact contract should be required before public wording?

## 9. Review Debt Classification

This section asks Antigravity to classify debt, not just review one file.

### 9.1 Debt That Should Block Public V4.0 Tag Until Reviewed

These are the highest-priority items.

| Debt | Path | Why blocking |
| --- | --- | --- |
| Final release external review | `future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md` | Public tag still lacks external release authorization. |
| Final evidence manifest after deltas | `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md` | Manifest controls the release packet; should be reviewed. |
| Goal4771 full V4 gate after Barnes-Hut delta | `future/v4/reviews/v4_goal4771_full_v4_gate_after_barnes_hut_delta_review_debt_2026-06-26.md` | Confirms manifest expansion and 632-test V4 local gate. |
| Current V4 public status/docs | `docs/current_v4_status.md`, `docs/app_level_benchmark_summary.md`, `README.md` | These are user-facing claims. |
| This Gemini/Antigravity debt packet | this file | Consolidates the missing external review seat. |

### 9.2 Debt That Blocks Specific Barnes-Hut / Paper-Reproduction Wording

These should not necessarily block a bounded V4.0 tag if V4.0 does not claim
public RT-BarnesHut paper reproduction, but they do block any such wording.

| Debt | Path | Current status |
| --- | --- | --- |
| Goal4760 author contract gate | `future/v4/reviews/v4_goal4760_rt_barneshut_author_contract_gate_review_debt_2026-06-26.md` | Contract review debt. |
| Goal4761 external author route | `future/v4/reviews/v4_goal4761_rt_barneshut_external_author_rt_core_route_review_debt_2026-06-26.md` | Author-binary wrapper/evidence debt. |
| Goal4762 feasibility gate | `future/v4/reviews/v4_goal4762_rt_barneshut_native_feasibility_gate_review_debt_2026-06-26.md` | Historical step; likely superseded by Goal4765+. |
| Goal4763 ABI first slice | `future/v4/reviews/v4_goal4763_rt_barneshut_native_abi_first_slice_review_debt_2026-06-26.md` | Historical step; likely superseded by runnable route. |
| Goal4764 host fallback checksum route | `future/v4/reviews/v4_goal4764_rt_barneshut_native_fallback_checksum_route_review_debt_2026-06-26.md` | Historical step; superseded by RT-core candidate for performance, still useful for checksum. |
| Goal4765 native RT-core candidate | `future/v4/reviews/v4_goal4765_rt_barneshut_native_rt_core_candidate_review_debt_2026-06-26.md` | Candidate correctness/claim-boundary review. |
| Goal4766 benchmark-ready scale gate | `future/v4/reviews/v4_goal4766_rt_barneshut_benchmark_ready_scale_gate_review_debt_2026-06-26.md` | 32768/1M scale evidence review. |
| Goal4767 10M scale gate | `future/v4/reviews/v4_goal4767_rt_barneshut_10m_scale_gate_review_debt_2026-06-26.md` | 10M run, later denominator corrected by Goal4769. |
| Goal4768 preprocessing/sort bottleneck | `future/v4/reviews/v4_goal4768_rt_barneshut_preprocessing_sort_bottleneck_review_debt_2026-06-26.md` | Identifies phase accounting issue. |
| Goal4769 author phase accounting | `future/v4/reviews/v4_goal4769_rt_barneshut_author_phase_accounting_review_debt_2026-06-26.md` | Corrects denominator and should be reviewed. |
| Goal4770 release packet delta | `future/v4/reviews/v4_goal4770_rt_barneshut_release_packet_delta_review_debt_2026-06-26.md` | Updates release packet interpretation; should be reviewed. |
| Goal4772 four-way fair compare | `future/v4/reviews/v4_goal4772_rt_barneshut_four_way_fair_compare_review_debt_2026-06-26.md` | Critical fairness/route-absence review. |

Reviewer requested classification:

- Which of these are superseded by later evidence?
- Which remain blocking only for RT-BarnesHut/paper-reproduction wording?
- Which, if any, must block the entire public V4.0 tag?

### 9.3 Debt That Appears Superseded By Goal4756/4757/4759/4771

These older release-candidate debts should be spot-audited, but the main claim
is that they are superseded by the complete app matrix and final manifest.

Representative paths:

| Area | Representative paths |
| --- | --- |
| Old Goal4720-4722 release-candidate guardrail/package cleanup | `future/v4/reviews/v4_goal4720_release_candidate_guardrail_convergence_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4722_clean_package_release_gate_review_debt_2026-06-26.md` |
| Goal4723-4731 early full-app protocol/matrix rows | `future/v4/reviews/v4_goal4723_complete_10_app_protocol_freeze_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4730_complete_10_app_matrix_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4731_post_matrix_release_decision_review_debt_2026-06-26.md` |
| Goal4732-4739 app-row repairs/deltas | `future/v4/reviews/v4_goal4732_raydb_device_output_route_repair_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4733_triangle_v3_regression_resolution_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4737_post_repair_app_matrix_delta_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4739_post_raydb_repair_app_matrix_delta_review_debt_2026-06-26.md` |
| Goal4740-4746 framing/docs/local gates | `future/v4/reviews/v4_goal4742_current_release_framing_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4743_public_docs_current_framing_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4744_full_v4_local_gate_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4746_final_release_candidate_review_packet_review_debt_2026-06-26.md` |
| Goal4749-4754 final RT-core protocol/superset/matrix | `future/v4/reviews/v4_goal4749_final_rt_core_protocol_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4751_superset_compatibility_review_debt_2026-06-26.md`, `future/v4/reviews/v4_goal4753_4754_full_rt_core_matrix_review_debt_2026-06-26.md` |

Requested Antigravity action:

```text
Please decide whether Goal4756/4757/4759/4771 supersede these older debts for
final release purposes. If any old debt still contains a unique unresolved
blocker, name it precisely.
```

### 9.4 Historical Scorecard Debt Already Reviewed By Antigravity

This group should not be reopened unless Antigravity finds a specific
contradiction with the current packet.

Source:

- `future/v4/reviews/v4_remaining_debt_after_antigravity_scorecard_review_and_forward_message_2026-06-24.md`
- `future/v4/reviews/antigravity_v4_goal4626_4632_scorecard_debt_review_2026-06-24.md`

Recorded status:

```text
All 9 substantive Goal4626-4632 scorecard review-debt items were recommended
for close_debt by Antigravity.
```

Requested Antigravity action:

```text
Do not re-review this whole historical set unless a current release claim
depends on one of those old rows in a way not covered by Goal4756/4759.
```

### 9.5 Tier-3 / Callback Debt

Tier-3 work produced useful spike evidence, but V4.0 public support for
arbitrary callbacks is not authorized.

Representative debt paths:

- `future/v4/reviews/v4_goal4685_tier3_wrapper_abi_protocol_review_debt_2026-06-25.md`
- `future/v4/reviews/v4_goal4688_tier3_module_link_probe_review_debt_2026-06-25.md`
- `future/v4/reviews/v4_goal4691_tier3_overhead_measurement_review_debt_2026-06-25.md`
- `future/v4/reviews/v4_goal4696_tier3_productization_decision_review_debt_2026-06-25.md`
- `future/v4/reviews/v4_goal4716_custom_predicate_early_exit_productization_review_debt_2026-06-26.md`
- `future/v4/reviews/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_review_debt_2026-06-26.md`

Current interpretation:

- arbitrary Python callbacks: not supported;
- raw OptiX callback support: not supported;
- Tier-3/PTX public support: not supported in V4.0;
- constrained Numba custom predicate early-exit workflow: measured bounded V4
  workflow evidence, not arbitrary callback support.

Requested Antigravity action:

```text
Confirm that unresolved Tier-3 debts do not block a bounded V4.0 tag as long as
public V4.0 wording says Tier-3/arbitrary callback support is not included.
If any Tier-3 file contradicts this boundary, identify it.
```

## 10. Required Review Questions

Please answer each question explicitly.

1. **Release scope:** Is the current V4.0 candidate honestly framed as a Python
   eDSL/operator-pushdown release candidate and V2/V3 superset?
2. **Performance truth:** Does the 10-app matrix support the claim "two material
   hot-path candidate wins over V2.14 and parity/control elsewhere"?
3. **No overclaim:** Do the current docs avoid "all apps faster", broad
   V4-over-V2, broad V4-over-V3, near-OptiX, or unbounded high-performance
   wording?
4. **Benchmark fairness:** Is the Goal4756 matrix fair enough for user-facing
   benchmark reporting, with NVIDIA RT-core/OptiX as the primary denominator
   and no `n/a` rows?
5. **V4 vs V2/V3:** Is it acceptable that V4 includes V2/V3 inherited routes
   as current V4 compatibility routes, while only fresh/measured mechanisms get
   new V4 speed credit?
6. **Barnes-Hut delta:** Is the Goal4770/4772 Barnes-Hut evidence correctly
   treated as supplemental paper-reproduction engineering evidence, not as
   public paper-reproduction authorization?
7. **RayJoin split:** Is the benchmark-vs-paper-reproduction classification for
   RayJoin correct?
8. **Review debt closure:** Which debts in section 9 must remain open before a
   public V4.0 tag, and which can be closed/superseded?
9. **Public tag:** Is the V4.0 public tag now approvable? If not, list exact
   blocking fixes.
10. **Reviewer role:** Can Antigravity serve as the currently available
    external reviewer for the Gemini review debt seat, given Gemini is
    unavailable and repeated Gemini probing is prohibited?

## 11. Requested Verdict Labels

Please choose exactly one top-level verdict:

- `approve_close_gemini_debt_and_allow_v4_0_public_tag`
- `approve_close_gemini_debt_but_require_claude_or_release_owner_final_tag`
- `approve_with_required_wording_or_evidence_amendments`
- `block_public_tag_pending_specific_fixes`
- `reject_release_reframe_required`

If choosing any verdict except the first, list the exact fixes or missing
reviews required.

## 12. Non-Authorization

This review-debt packet does not authorize:

- public V4.0 tag by itself;
- broad V4 speedup wording;
- "all benchmark apps are faster" wording;
- broad V4-over-V2.14 or V4-over-V3 wording;
- public true-zero-copy claims;
- no-copy or device-resident tree-build claims;
- arbitrary callback support;
- raw OptiX callback support;
- Tier-3/PTX public support;
- C ABI, embedding, or non-Python host claims;
- public RT-BarnesHut paper-reproduction wording;
- public RayJoin paper-reproduction wording from the current V4 benchmark row.

## 13. Forward Message To Antigravity

You can paste this message to Antigravity:

```text
Please review the full V4 Gemini review-debt packet:

future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md

Context: Gemini CLI is unavailable and should not be repeatedly probed. We need
Antigravity to act as the available external reviewer for the Gemini-style
review debt seat.

Please read the packet and the core evidence paths it lists, then return one of
the required verdict labels:

- approve_close_gemini_debt_and_allow_v4_0_public_tag
- approve_close_gemini_debt_but_require_claude_or_release_owner_final_tag
- approve_with_required_wording_or_evidence_amendments
- block_public_tag_pending_specific_fixes
- reject_release_reframe_required

The key things to audit are:

1. whether the V4.0 release candidate is honestly framed as a Python
   eDSL/operator-pushdown release candidate and V2/V3 superset;
2. whether the Goal4756 10-app V2.14/V3.0.2/V4.0 RT-core matrix is complete and
   fair enough for user-facing benchmark reporting;
3. whether the docs avoid broad/unbounded speedup claims;
4. whether Goal4770/4772 Barnes-Hut evidence should remain supplemental rather
   than public paper-reproduction wording;
5. which old review debts are superseded by Goal4756/4759/4771 and which still
   block public tagging.

Please be strict. If public tag should remain blocked, name exact blockers.
```

## 14. Goal-Level Decision Audit

1. Was I being foolish?
   - Not in creating this packet. The foolish path would be repeatedly probing
     Gemini or pretending that missing Gemini review is already closed.

2. What action would make this foolish?
   - Writing another small fragmented review request that forces the user or
     reviewer to reconstruct the whole V4 state from dozens of debt files.

3. Is there another path?
   - Yes: consolidate the current release state, evidence, old/superseded debt,
     and remaining blocking questions into one full-coverage review packet.

4. Can I now try the different path that actually solves the problem?
   - Yes. This file is the consolidated packet for Antigravity review, while
     Gemini remains unavailable and should not be retried without a user-approved
     solution.
