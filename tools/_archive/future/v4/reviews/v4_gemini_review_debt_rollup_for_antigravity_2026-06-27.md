# V4 Gemini/External Review Debt Rollup For Antigravity

Date: 2026-06-27

Status: `rollup_created_for_antigravity_review__do_not_retry_gemini_cli`

Reviewer requested: Antigravity, acting as the available external reviewer for
Gemini-style review debt because Gemini CLI review is currently unavailable and
the user instructed the main agent not to keep probing Gemini.

## 0. Why This File Exists

From 2026-06-25 through 2026-06-27, V4 accumulated many small review-debt
records while Gemini was unavailable. A later full-coverage Gemini-style packet
was reviewed by Antigravity, but new public-surface/documentation debt appeared
after that review.

This file consolidates the review-debt state so the next Antigravity review can
make one clear classification instead of reconstructing the project from many
small files.

Local inventory:

| Item | Count |
| --- | ---: |
| `review_debt` files dated 2026-06-25 through 2026-06-27 under `future/v4/reviews/` | 111 |
| Antigravity review/attempt files dated 2026-06-25 through 2026-06-27 under `future/v4/reviews/` | 80 |

## 1. Existing Antigravity Closure Already On Record

Do not ignore this record:

- packet:
  `future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md`
- Antigravity result:
  `future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md`

Recorded verdict:

```text
approve_close_gemini_debt_and_allow_v4_0_public_tag
```

Important classification from that review:

1. Public V4.0 tag was authorized under bounded framing.
2. Older Goal4720-4754 release/matrix debts were superseded by the complete
   Goal4756 matrix and Goal4759 final manifest.
3. Goal4626-4632 scorecard debts were already closed by the earlier
   Antigravity scorecard review.
4. Tier-3/callback debts do not block V4.0 because V4.0 docs explicitly do not
   claim arbitrary callback, raw OptiX callback, or Tier-3/PTX public support.
5. RT-BarnesHut/paper-reproduction debts remain open only to block specific
   public paper-reproduction/no-copy/Barnes-Hut claims.

## 2. Current Action Items For Antigravity

Please review these first. They are the current open items after the full
Gemini-style closure.

| Priority | Debt | Path | Requested decision |
| --- | --- | --- | --- |
| P0 | Public documentation fix response after external block | `history/v4_0_release_audit_2026-06-27/call_for_review_v4_doc_audit_fix_response_2026-06-27.md` | Decide whether the P0 doc/tutorial leakage findings are fixed. |
| P0 | Goal4777 public-surface release audit | `future/v4/reviews/v4_goal4777_public_surface_review_debt_2026-06-27.md`; primary packet `future/v4/reviews/call_for_review_v4_goal4777_public_surface_main_release_audit_2026-06-27.md` | Decide whether the public surface is coherent after the pushed `v4.0.0` tag. |
| P1 | Confirm old Gemini debt closure remains valid after doc fixes | This rollup plus `antigravity_v4_gemini_full_coverage_review_2026-06-27.md` | Decide whether any old debt must be reopened because of current public-doc changes. |

Requested top-level verdict labels:

- `approve_current_external_debt_closed_except_specific_claim_blocks`
- `approve_with_minor_public_doc_edits`
- `block_public_surface_pending_specific_fixes`
- `reopen_gemini_debt_with_named_blockers`

If choosing any verdict except the first, name exact files and exact blocking
sentences or missing evidence.

## 3. Still Open, But Only For Specific Barnes-Hut/Paper-Reproduction Wording

These debts do not block a bounded V4.0 public tag according to the full
Antigravity Gemini-debt review. They do block public claims such as
"RTDL fully reproduces RT-BarnesHut", "V2/V3/V4 all implement the author route",
"no-copy Barnes-Hut tree build", or broad Barnes-Hut paper speedup wording.

| Debt | File | Current rollup classification |
| --- | --- | --- |
| Goal4760 author contract gate | `future/v4/reviews/v4_goal4760_rt_barneshut_author_contract_gate_review_debt_2026-06-26.md` | Specific-claim blocker only. |
| Goal4761 external author route | `future/v4/reviews/v4_goal4761_rt_barneshut_external_author_rt_core_route_review_debt_2026-06-26.md` | Specific-claim blocker only. |
| Goal4762 native feasibility gate | `future/v4/reviews/v4_goal4762_rt_barneshut_native_feasibility_gate_review_debt_2026-06-26.md` | Superseded by later runnable route for V4 tag; specific-claim history remains. |
| Goal4763 native ABI first slice | `future/v4/reviews/v4_goal4763_rt_barneshut_native_abi_first_slice_review_debt_2026-06-26.md` | Superseded by later runnable route for V4 tag; specific-claim history remains. |
| Goal4764 host fallback checksum route | `future/v4/reviews/v4_goal4764_rt_barneshut_native_fallback_checksum_route_review_debt_2026-06-26.md` | Useful checksum history; specific-claim blocker only. |
| Goal4765 native RT-core candidate | `future/v4/reviews/v4_goal4765_rt_barneshut_native_rt_core_candidate_review_debt_2026-06-26.md` | Specific-claim blocker only. |
| Goal4766 benchmark-ready scale gate | `future/v4/reviews/v4_goal4766_rt_barneshut_benchmark_ready_scale_gate_review_debt_2026-06-26.md` | Specific-claim blocker only. |
| Goal4767 10M scale gate | `future/v4/reviews/v4_goal4767_rt_barneshut_10m_scale_gate_review_debt_2026-06-26.md` | Specific-claim blocker only; later denominator corrected by Goal4769. |
| Goal4768 preprocessing/sort bottleneck | `future/v4/reviews/v4_goal4768_rt_barneshut_preprocessing_sort_bottleneck_review_debt_2026-06-26.md` | Specific-claim blocker only. |
| Goal4769 author phase accounting | `future/v4/reviews/v4_goal4769_rt_barneshut_author_phase_accounting_review_debt_2026-06-26.md` | Important if public author-comparison wording is desired. |
| Goal4770 release packet delta | `future/v4/reviews/v4_goal4770_rt_barneshut_release_packet_delta_review_debt_2026-06-26.md` | Specific-claim blocker only. |
| Goal4771 full V4 gate after Barnes-Hut delta | `future/v4/reviews/v4_goal4771_full_v4_gate_after_barnes_hut_delta_review_debt_2026-06-26.md` | Closed for V4 tag by full-coverage Antigravity review; still relevant evidence. |
| Goal4772 four-way fair compare | `future/v4/reviews/v4_goal4772_rt_barneshut_four_way_fair_compare_review_debt_2026-06-26.md` | Specific-claim blocker only. |

Antigravity question: Do you agree that these remain specific-claim blockers
only, not bounded V4.0 tag blockers?

## 4. Superseded Release/Matrix Debt From 2026-06-26

The full Antigravity Gemini-debt review classified these as superseded by the
complete 30-row RT-core matrix, final manifest, and full V4 local gate unless a
reviewer finds a unique unresolved blocker.

| Debt | File | Rollup classification |
| --- | --- | --- |
| Goal4711 custom scored app focused POD | `future/v4/reviews/v4_goal4711_custom_scored_app_focused_pod_review_debt_2026-06-26.md` | Superseded/nonblocking. |
| Goal4712 next lever after custom scored failure | `future/v4/reviews/v4_goal4712_next_lever_after_custom_scored_failure_review_debt_2026-06-26.md` | Superseded/nonblocking. |
| Goal4713 custom predicate protocol | `future/v4/reviews/v4_goal4713_custom_predicate_early_exit_protocol_review_debt_2026-06-26.md` | Superseded by measured custom-predicate workflow docs. |
| Goal4714 custom predicate smoke POD | `future/v4/reviews/v4_goal4714_custom_predicate_early_exit_smoke_pod_review_debt_2026-06-26.md` | Superseded by serious-scale validation. |
| Goal4715 custom predicate timing POD | `future/v4/reviews/v4_goal4715_custom_predicate_early_exit_timing_pod_review_debt_2026-06-26.md` | Superseded by serious-scale validation. |
| Goal4716 custom predicate productization | `future/v4/reviews/v4_goal4716_custom_predicate_early_exit_productization_review_debt_2026-06-26.md` | Nonblocking because arbitrary/Tier-3 callbacks are not public V4.0 support. |
| Goal4717 custom predicate serious-scale validation | `future/v4/reviews/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_review_debt_2026-06-26.md` | Evidence included in current V4 bounded workflow claim. |
| Goal4718 release matrix after custom predicate | `future/v4/reviews/v4_goal4718_release_matrix_after_custom_predicate_review_debt_2026-06-26.md` | Superseded by later complete matrix. |
| Goal4719 public docs/examples cleanup | `future/v4/reviews/v4_goal4719_public_docs_examples_release_candidate_cleanup_review_debt_2026-06-26.md` | Superseded by Goal4777 and the 2026-06-27 doc audit fix response. |
| Goal4720 guardrail convergence | `future/v4/reviews/v4_goal4720_release_candidate_guardrail_convergence_review_debt_2026-06-26.md` | Superseded by final manifest/tag authorization. |
| Goal4722 clean package release gate | `future/v4/reviews/v4_goal4722_clean_package_release_gate_review_debt_2026-06-26.md` | Superseded by clean checkout/wheel smoke evidence. |
| Goal4723 complete 10-app protocol freeze | `future/v4/reviews/v4_goal4723_complete_10_app_protocol_freeze_review_debt_2026-06-26.md` | Superseded by final 30-row matrix. |
| Goal4724 remaining 5-app route-gap audit | `future/v4/reviews/v4_goal4724_remaining_5_app_route_gap_audit_review_debt_2026-06-26.md` | Superseded by full matrix and V4-as-superset framing. |
| Goal4725 RTNN measured no-win row | `future/v4/reviews/v4_goal4725_rtnn_measured_no_win_row_review_debt_2026-06-26.md` | Superseded by final app-level matrix. |
| Goal4726 robot collision partial/no-go row | `future/v4/reviews/v4_goal4726_robot_collision_partial_no_go_row_review_debt_2026-06-26.md` | Superseded by final same-RT-core matrix row. |
| Goal4727 contact manifold no-go row | `future/v4/reviews/v4_goal4727_contact_manifold_no_go_row_review_debt_2026-06-26.md` | Superseded by final matrix row. |
| Goal4728 spatial RayJoin no-route blocker row | `future/v4/reviews/v4_goal4728_spatial_rayjoin_no_route_blocker_row_review_debt_2026-06-26.md` | Superseded by generated shape-pair matrix row and RayJoin classification. |
| Goal4729 Barnes-Hut deferred/subprobe row | `future/v4/reviews/v4_goal4729_barnes_hut_deferred_subprobe_row_review_debt_2026-06-26.md` | Superseded by final matrix row; paper wording remains separately blocked. |
| Goal4730 complete 10-app matrix | `future/v4/reviews/v4_goal4730_complete_10_app_matrix_review_debt_2026-06-26.md` | Superseded by Goal4756 final matrix. |
| Goal4731 post-matrix release decision | `future/v4/reviews/v4_goal4731_post_matrix_release_decision_review_debt_2026-06-26.md` | Superseded by final release packet and Antigravity full review. |
| Goal4732 RayDB device-output route repair | `future/v4/reviews/v4_goal4732_raydb_device_output_route_repair_review_debt_2026-06-26.md` | Superseded by final matrix. |
| Goal4733 triangle V3 regression resolution | `future/v4/reviews/v4_goal4733_triangle_v3_regression_resolution_review_debt_2026-06-26.md` | Superseded by final matrix. |
| Goal4734 RTDBSCAN generic continuation no-go | `future/v4/reviews/v4_goal4734_rt_dbscan_generic_continuation_no_go_review_debt_2026-06-26.md` | Superseded/nonblocking; no broad speedup claim. |
| Goal4735 fresh generic operator target selection | `future/v4/reviews/v4_goal4735_fresh_generic_operator_target_selection_review_debt_2026-06-26.md` | Superseded/nonblocking. |
| Goal4736 Barnes-Hut complete workflow | `future/v4/reviews/v4_goal4736_barnes_hut_complete_workflow_review_debt_2026-06-26.md` | Superseded by final matrix; paper wording remains separately blocked. |
| Goal4737 post-repair app matrix delta | `future/v4/reviews/v4_goal4737_post_repair_app_matrix_delta_review_debt_2026-06-26.md` | Superseded by final matrix. |
| Goal4738 RayDB hotpath boundary repair | `future/v4/reviews/v4_goal4738_raydb_hotpath_materialization_boundary_repair_review_debt_2026-06-26.md` | Superseded by final matrix. |
| Goal4739 post-RayDB repair app matrix delta | `future/v4/reviews/v4_goal4739_post_raydb_repair_app_matrix_delta_review_debt_2026-06-26.md` | Superseded by final matrix. |
| Goal4740 robot collision boundary recheck | `future/v4/reviews/v4_goal4740_robot_collision_boundary_recheck_review_debt_2026-06-26.md` | Superseded by final matrix. |
| Goal4741 spatial RayJoin route reopen decision | `future/v4/reviews/v4_goal4741_spatial_rayjoin_route_reopen_decision_review_debt_2026-06-26.md` | Superseded by final matrix and RayJoin split. |
| Goal4742 current release framing | `future/v4/reviews/v4_goal4742_current_release_framing_review_debt_2026-06-26.md` | Superseded by public status/docs after tag. |
| Goal4743 public docs current framing | `future/v4/reviews/v4_goal4743_public_docs_current_framing_review_debt_2026-06-26.md` | Superseded by 2026-06-27 doc audit fix response. |
| Goal4744 full V4 local gate | `future/v4/reviews/v4_goal4744_full_v4_local_gate_review_debt_2026-06-26.md` | Superseded by later full V4 gates. |
| Goal4745 machine release decision refresh | `future/v4/reviews/v4_goal4745_machine_release_decision_refresh_review_debt_2026-06-26.md` | Superseded by release-owner status after Antigravity review. |
| Goal4746 final release-candidate review packet | `future/v4/reviews/v4_goal4746_final_release_candidate_review_packet_review_debt_2026-06-26.md` | Superseded by final release packet. |
| Goal4749 final RT-core protocol | `future/v4/reviews/v4_goal4749_final_rt_core_protocol_review_debt_2026-06-26.md` | Superseded by final 30-row matrix. |
| Goal4750 unified runner | `future/v4/reviews/v4_goal4750_unified_runner_review_debt_2026-06-26.md` | Superseded by final public front door and matrix. |
| Goal4751 superset compatibility | `future/v4/reviews/v4_goal4751_superset_compatibility_review_debt_2026-06-26.md` | Superseded by current V4-as-V2/V3-superset docs. |
| Goal4753-4754 full RT-core matrix and analysis | `future/v4/reviews/v4_goal4753_4754_full_rt_core_matrix_review_debt_2026-06-26.md` | Superseded by Goal4756 final matrix. |
| Goal4757 final release external review | `future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md` | Closed by full Antigravity Gemini-debt packet. |

Antigravity question: Do you agree that none of these should remain a public
V4.0 tag blocker after the final matrix, manifest, and published-tag public
surface audit?

## 5. Tier-3 / Callback / Experimental Debt

These debts remain useful engineering history, but they do not block V4.0
because the public release does not claim arbitrary callbacks, raw OptiX
callback support, or Tier-3/PTX public support.

| Debt | File | Rollup classification |
| --- | --- | --- |
| Goal4685 Tier-3 wrapper ABI protocol | `future/v4/reviews/v4_goal4685_tier3_wrapper_abi_protocol_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4686 Tier-3 wrapper ABI local scaffold | `future/v4/reviews/v4_goal4686_tier3_wrapper_abi_local_scaffold_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4687 Tier-3 wrapper compile probe | `future/v4/reviews/v4_goal4687_tier3_wrapper_compile_probe_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4688 Tier-3 module-link probe | `future/v4/reviews/v4_goal4688_tier3_module_link_probe_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4689 Tier-3 minimal launch probe | `future/v4/reviews/v4_goal4689_tier3_minimal_launch_probe_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4690 Tier-3 overhead protocol | `future/v4/reviews/v4_goal4690_tier3_overhead_protocol_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4691 Tier-3 overhead measurement | `future/v4/reviews/v4_goal4691_tier3_overhead_measurement_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4692 Tier-3 support decision | `future/v4/reviews/v4_goal4692_tier3_support_decision_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4693 specialized hit callback probe | `future/v4/reviews/v4_goal4693_specialized_hit_callback_probe_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4694 specialized hit overhead protocol | `future/v4/reviews/v4_goal4694_specialized_hit_overhead_protocol_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4695 specialized hit overhead measurement | `future/v4/reviews/v4_goal4695_specialized_hit_overhead_measurement_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4696 Tier-3 productization decision | `future/v4/reviews/v4_goal4696_tier3_productization_decision_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4697 specialized Tier-3 API contract | `future/v4/reviews/v4_goal4697_specialized_tier3_api_contract_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4698 specialized Tier-3 compile cache | `future/v4/reviews/v4_goal4698_specialized_tier3_compile_cache_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4699 specialized Tier-3 app-route protocol | `future/v4/reviews/v4_goal4699_specialized_tier3_app_route_protocol_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4700 specialized Tier-3 app-route POD | `future/v4/reviews/v4_goal4700_specialized_tier3_app_route_pod_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4701 specialized Tier-3 support candidate | `future/v4/reviews/v4_goal4701_specialized_tier3_support_candidate_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4702 specialized Tier-3 reliability protocol | `future/v4/reviews/v4_goal4702_specialized_tier3_reliability_protocol_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4703 specialized Tier-3 reliability matrix | `future/v4/reviews/v4_goal4703_specialized_tier3_reliability_matrix_pod_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4704 specialized Tier-3 support wording | `future/v4/reviews/v4_goal4704_specialized_tier3_support_wording_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4705 source/PTX cache stability | `future/v4/reviews/v4_goal4705_source_ptx_cache_stability_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4706 negative validation/docs gate | `future/v4/reviews/v4_goal4706_negative_validation_docs_gate_review_debt_2026-06-25.md` | V4.x/research; nonblocking. |
| Goal4707 consolidated specialized Tier-3 ledger | `future/v4/reviews/v4_goal4707_specialized_tier3_review_debt_ledger_2026-06-25.md` | V4.x/research; nonblocking. |

Antigravity question: Do you still agree with the 2026-06-27 full-coverage
review that this group does not block V4.0 if public docs continue to exclude
Tier-3/callback support?

## 6. Earlier 2026-06-25 Goal-Completion Debt

These are lower-level construction debts from the route/partner/catalog work.
They appear superseded or nonblocking for V4.0 by later full matrix evidence,
catalog gates, and the full Antigravity review.

| Debt | File | Rollup classification |
| --- | --- | --- |
| Goal4633 weighted-sum promotion completion | `future/v4/reviews/goal4633_completion_consensus_and_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4634 coverage refresh | `future/v4/reviews/goal4634_completion_consensus_and_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4635 component-union promotion | `future/v4/reviews/goal4635_component_union_promotion_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4647 partner inventory | `future/v4/reviews/goal4647_completion_consensus_and_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4652 app route binding | `future/v4/reviews/goal4652_completion_consensus_and_review_debt_2026-06-25.md` | Superseded by current app matrix and compatibility catalog. |
| Goal4653 full-app protocol freeze | `future/v4/reviews/goal4653_completion_consensus_and_review_debt_2026-06-25.md` | Superseded by final matrix. |
| Goal4654 full-app POD benchmark | `future/v4/reviews/goal4654_completion_consensus_and_review_debt_2026-06-25.md` | Superseded by final matrix. |
| Goal4655 benchmark analysis | `future/v4/reviews/goal4655_completion_consensus_and_review_debt_2026-06-25.md` | Superseded by final matrix/readout. |
| Goal4656 public docs machine boundary | `future/v4/reviews/goal4656_completion_consensus_and_review_debt_2026-06-25.md` | Superseded by Goal4777 and doc audit fix. |
| Goal4657 external review/no release authorization | `future/v4/reviews/goal4657_external_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded by final Antigravity review and release-owner status. |
| Goal4658 completion review debt | `future/v4/reviews/goal4658_completion_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4659 Hausdorff official route | `future/v4/reviews/goal4659_completion_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded by matrix and semantic notes. |
| Goal4666 | `future/v4/reviews/goal4666_completion_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4667 | `future/v4/reviews/goal4667_completion_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4668 | `future/v4/reviews/goal4668_completion_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4669 | `future/v4/reviews/goal4669_completion_review_debt_and_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4670 | `future/v4/reviews/goal4670_completion_review_debt_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4671 | `future/v4/reviews/goal4671_completion_review_debt_no_release_authorization_2026-06-25.md` | Superseded/nonblocking. |
| Goal4673 target design | `future/v4/reviews/v4_goal4673_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4674 aggregate-frontier static protocol | `future/v4/reviews/v4_goal4674_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4675 aggregate-frontier prepared runner | `future/v4/reviews/v4_goal4675_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4676 aggregate-frontier POD/protocol | `future/v4/reviews/v4_goal4676_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4677 aggregate-frontier promotion | `future/v4/reviews/v4_goal4677_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4678 ranked-summary disposition | `future/v4/reviews/v4_goal4678_review_debt_2026-06-25.md` | Nonblocking because ranked summary is not a V4.0 release surface. |
| Goal4679 relation topology target | `future/v4/reviews/v4_goal4679_relation_topology_target_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4680 shape-pair protocol | `future/v4/reviews/v4_goal4680_shape_pair_relation_protocol_review_debt_2026-06-25.md` | Superseded by final matrix. |
| Goal4681 shape-pair POD benchmark | `future/v4/reviews/v4_goal4681_shape_pair_relation_pod_benchmark_review_debt_2026-06-25.md` | Superseded by final matrix. |
| Goal4682 next target after shape-pair | `future/v4/reviews/v4_goal4682_next_target_after_shape_pair_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4683 contact/witness design audit | `future/v4/reviews/v4_goal4683_contact_witness_design_audit_review_debt_2026-06-25.md` | Superseded/nonblocking. |
| Goal4684 high-performance target reset | `future/v4/reviews/v4_goal4684_high_performance_target_reset_review_debt_2026-06-25.md` | Superseded/nonblocking. |

Antigravity question: If any row in this section still contains a unique
unresolved blocker, please name the exact file and the exact blocker.

## 7. What Must Not Be Authorized By This Rollup

This rollup does not authorize:

- broad all-app speedup wording;
- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- whole-application high-performance wording;
- public true-zero-copy claims;
- Tier-3 callback/PTX public support;
- raw OptiX callback support;
- broad CuPy performance claims;
- embedding, C ABI, or non-Python host binding claims;
- public RT-BarnesHut paper-reproduction speedup claims;
- moving, deleting, or force-updating the already pushed `v4.0.0` tag.

## 8. Requested Antigravity Response

Please answer:

1. Are the two active P0 items in Section 2 approved, amended, or blocked?
2. Do you confirm that the 2026-06-27 Antigravity full-coverage review still
   closes the Gemini review-debt seat for the bounded V4.0 tag?
3. Do you confirm that Section 3 remains specific-claim-only Barnes-Hut debt,
   not a V4.0 tag blocker?
4. Do you confirm that Sections 4-6 are superseded/nonblocking for current V4.0
   public release purposes?
5. If anything remains blocking, list exact file paths and exact required fixes.

## 9. Short Forward Message

```text
Please review this consolidated V4 Gemini/external review-debt rollup:

future/v4/reviews/v4_gemini_review_debt_rollup_for_antigravity_2026-06-27.md

It inventories the 2026-06-25..27 Gemini-style review debts, the existing
Antigravity full-coverage closure, the still-open Barnes-Hut specific-claim
debt, and the new public-surface/doc-audit debt from 2026-06-27.

Please return one top-level verdict:
- approve_current_external_debt_closed_except_specific_claim_blocks
- approve_with_minor_public_doc_edits
- block_public_surface_pending_specific_fixes
- reopen_gemini_debt_with_named_blockers

If blocked, name exact files and exact fixes.
```

## 10. Goal-Level Decision Audit

1. Was I being foolish?
   - The prior failure mode would be foolish: creating another small review
     request without inventorying what Antigravity had already closed.

2. What action would make this foolish?
   - Reopening all 111 review-debt files as if none were superseded, or ignoring
     the existing `approve_close_gemini_debt_and_allow_v4_0_public_tag` verdict.

3. Is there another path?
   - Yes: classify debts by current release effect: active public-surface debt,
     specific-claim-only Barnes-Hut debt, superseded matrix/release debt, and
     nonblocking Tier-3 research debt.

4. Can I now take the path that solves the problem?
   - Yes. This rollup gives Antigravity one review target and preserves the
     exact files needed for spot-audit.
