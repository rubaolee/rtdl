# Goal5429 - X-HD Exact Input Or Exact-Equivalence Decision Refresh

## Verdict

```text
exact_input_or_equivalence_decision_refreshed_after_goal5428__no_route_work
```

Goal5429 refreshes the full-paper reproduction decision after Goal5428 expanded
the current Level-B matrix.  It performs no POD execution, no author execution,
no RTDL execution, and no route optimization.

The decision is:

```text
Full X-HD paper reproduction is still blocked by exact input artifacts or an
explicit exact-equivalence acceptance.  The next useful work is review,
provenance, or exact-equivalence, not route tuning.
```

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5429.exact_input_or_equivalence_decision_refresh.v1
status = exact_input_or_equivalence_decision_refreshed_after_goal5428__no_route_work
recommended_next_goal = Goal5430_water_bg_exact_equivalence_review_packet_or_author_artifact_request
```

## Inputs

Goal5429 reads:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
```

Goal5428 provides the current Level-B evidence matrix:

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

Goal5324 provides the still-valid exact-input decision:

```text
full_reproduction_next_blocker = exact_input_artifacts_or_explicit_exact_equivalence_acceptance
more_route_performance_work_is_next = false
```

## Current Best Candidate

Goal5429 keeps WaterBodies->BlockGroups as the strongest current
exact-equivalence review candidate:

```text
row_id = geo_waterbodies_blockgroups
goal5428_row_id = geo_water_bg_full_public_paper_config
evidence_level = level_b_full_public_same_source_geo_not_exact_file_hash
```

Why it is strongest:

```text
WaterBodies and BlockGroups full-public MBRs match paper logs.
Point-count deltas are small compared with other geo rows.
Author paper-config rerun with n_points_cell=8 reproduces paper-log HDResult.
RTDL exact-witness float64 aligns with author/paper float32 within the declared numeric boundary.
```

Why it is not exact:

```text
No author WKT file hashes.
No proof that current ArcGIS services are the author's exact snapshot.
No byte-identical regeneration proof.
Remaining point-count deltas are nonzero.
```

## Exact Or Exact-Equivalence Gate

The only valid next paths beyond Level-B remain:

```text
obtain author input files/hashes or converted point-set artifacts
obtain byte-identical regeneration scripts and source snapshots
obtain external review accepting a deterministic public reconstruction as exact-equivalent for a bounded claim
otherwise keep the project at Level-B for these rows
```

Before exact-equivalence can even be considered, the public reconstruction must
have:

```text
pinned public source URL or archive identifier
source snapshot date/version/hash where applicable
deterministic conversion/export script in the repository
explicit geometry filtering/simplification/precision policy
generated input file sha256 recorded in artifact
author hd_exec rerun on generated inputs matches paper-log scalar within declared tolerance
RTDL route on the same generated inputs matches the author rerun within declared tolerance
external review explicitly accepts the generated public inputs as exact-equivalent or accepts a renamed bounded public-reconstruction claim
```

Not sufficient:

```text
matching point counts
matching MBRs
matching Gini/statistics
matching HDResult alone
matching author rerun on current public service snapshot
checked-in author logs
public repository source code without input hashes
```

## Branch Ranking

```text
1. strict_review_goals5424_5428_packet
2. author_artifact_or_hash_acquisition
3. water_bg_public_reconstruction_exact_equivalence_review_packet
4. same_input_author_rtdl_gate_after_new_artifacts
```

POD is not useful for the first three branches.  POD becomes useful only after
new exact artifacts arrive or after an accepted exact-equivalence reconstruction
needs author/RTDL verification.

## Rejected Paths

```text
route_micro_optimization = false
explicit_lb_or_row_identity_work = false
water_bg_exact_promotion_by_statistics_only = false
performance_ratio_from_goal5428 = false
```

Reasons:

```text
The blocker is input identity, not route timing.
The implementation-artifact parity line remains fail-closed.
Statistics and scalar matches do not prove exact dataset identity.
Author AvgTime, process wall, RTDL route wall, and RTDL total are separate denominators.
```

## Claim Boundary

Authorized:

```text
decision_refresh_claimed = true
level_b_matrix_current_claimed = true
```

Not authorized:

```text
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
author_rt_core_algorithm_equivalence_claimed = false
new_pod_execution_claimed = false
new_rtdl_route_code_added = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

This goal mentions explicit `-lb` only as a stopped line.  It does not start
row identity, hash parity, offload stream, or other app-artifact parity work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: exact-input / exact-equivalence decision packet; no app-artifact parity implementation
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: this goal keeps app-artifact parity fail-closed and redirects to provenance/equivalence.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
py -m unittest tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5427_water_bg_paper_config_consolidation_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

The known Windows Python prefix warning may appear and is not a failure if
tests pass.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5429_exact_input_or_equivalence_decision_refresh.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
tests/goal5429_exact_input_or_equivalence_decision_refresh_test.py
history/internal_docs/goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
history/internal_docs/call_for_review_goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5430_water_bg_exact_equivalence_review_packet_or_author_artifact_request
```

Goal5430 should either:

```text
prepare a strict exact-equivalence review packet for WaterBodies->BlockGroups
or prepare an author artifact/hash request packet
```

It must not:

```text
rerun the 873s-class Water/BG exact route without new artifacts
claim exact paper input
claim geo Figure 5 reproduction
publish author-vs-RTDL performance ratio
start route micro-optimization
reopen explicit -lb
```
