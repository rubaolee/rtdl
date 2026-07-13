# Call For Review - Goal5429 X-HD Exact Input Or Exact-Equivalence Decision Refresh

Please strictly review Goal5429.

This goal is a decision refresh after Goal5428.  It does **not** execute author
code, does **not** execute RTDL code, does **not** run POD, and does **not**
optimize route performance.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
tests/goal5429_exact_input_or_equivalence_decision_refresh_test.py
history/internal_docs/goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
history/internal_docs/call_for_review_goals5424_5428_xhd_water_bg_full_public_level_b_packet_2026-07-10.md
history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md
scripts/xhd_stop_loss_gate_check.py
```

## Summary To Attack

Goal5428 expanded the current X-HD Level-B evidence matrix:

```text
graphics_case_count = 3
graphics_route_result_count = 6
bounded_geo_case_count = 2
bounded_geo_route_result_count = 2
full_public_geo_case_count = 1
full_public_geo_route_result_count = 1
total_case_count = 6
total_route_result_count = 9
```

Goal5429 concludes that this does **not** change the full-paper blocker:

```text
full_reproduction_next_blocker = exact_input_artifacts_or_explicit_exact_equivalence_acceptance
more_route_performance_work_is_next = false
route_micro_optimization_authorized = false
explicit_lb_authorized = false
```

Goal5429 keeps WaterBodies->BlockGroups as the best current candidate for a
possible exact-equivalence review, but explicitly says it is still not exact:

```text
row_id = geo_waterbodies_blockgroups
goal5428_row_id = geo_water_bg_full_public_paper_config
evidence_level = level_b_full_public_same_source_geo_not_exact_file_hash
```

Why not exact:

```text
No author WKT file hashes.
No proof that current ArcGIS services are the author's exact snapshot.
No byte-identical regeneration proof.
Remaining point-count deltas are nonzero.
```

## Claim Boundary To Attack

Authorized:

```text
decision_refresh_claimed = true
level_b_matrix_current_claimed = true
```

Forbidden:

```text
exact_paper_dataset_reproduction_claimed
figure5_reproduction_claimed
full_xhd_paper_reproduction_claimed
performance_ratio_claimed
author_rt_core_algorithm_equivalence_claimed
new_pod_execution_claimed
new_rtdl_route_code_added
explicit_lb_reopened
route_micro_optimization_goal_authorized
```

## Stop-Loss Gate G-1

Goal5429 mentions explicit `-lb` only as a stopped line and does not start
app-artifact parity work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: exact-input / exact-equivalence decision packet; no app-artifact parity implementation
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Requested check: please verify this is a legitimate decision/provenance packet,
not a disguised continuation of row identity / hash parity / offload stream
work.

## Validation Commands Already Run

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
py -m unittest tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5427_water_bg_paper_config_consolidation_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5429_xhd_exact_input_or_equivalence_decision_refresh
```

Revise:

```text
revise_goal5429_xhd_exact_input_or_equivalence_decision_refresh
```

Block:

```text
block_goal5429_xhd_exact_input_or_equivalence_decision_refresh
```

## Review Questions

1. Does Goal5429 correctly preserve the Goal5428 Level-B matrix status as
   6 cases / 9 route results?
2. Does Goal5429 correctly identify the next full-paper blocker as exact input
   artifacts or explicit exact-equivalence acceptance?
3. Does Goal5429 correctly avoid treating route micro-optimization as the next
   paper-reproduction step?
4. Does Goal5429 correctly keep explicit `-lb` / row identity / app-artifact
   parity fail-closed?
5. Does Goal5429 correctly keep WaterBodies->BlockGroups below exact input
   status despite strong scalar evidence?
6. Is the exact-equivalence protocol strict enough, especially the rule that
   point counts, MBRs, and HDResult alone are not sufficient?
7. Does Goal5429 correctly avoid POD work until new artifacts or an accepted
   exact-equivalence reconstruction exists?
8. Does the builder remain decision-only, with no subprocess, no POD wrapper,
   no `hd_exec`, and no route execution?
9. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   work that should fail-close?
10. Is the recommended next goal correct: a Water/BG exact-equivalence review
    packet or author artifact/hash request, not route tuning?

## Expected Answer Shape

Please answer with:

```text
Verdict: <one requested label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```
