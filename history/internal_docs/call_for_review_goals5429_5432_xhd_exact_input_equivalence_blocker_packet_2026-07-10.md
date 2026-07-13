# Call For Review - Goals5429-5432 X-HD Exact-Input / Exact-Equivalence Blocker Packet

Please strictly review Goals5429-5432 as one X-HD full-reproduction blocker
node.

This packet is the current decision point after the expanded Level-B matrix.
It should answer whether the project has a legitimate path beyond Level-B
without new external evidence, or whether the only honest next movement is
external artifact / hash / exact-equivalence response.

## Files Under Review

Goal5429:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
history/internal_docs/goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
history/internal_docs/call_for_review_goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
tests/goal5429_exact_input_or_equivalence_decision_refresh_test.py
```

Goal5430:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
history/internal_docs/goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
history/internal_docs/call_for_review_goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
tests/goal5430_water_bg_exact_equivalence_packet_test.py
```

Goal5431:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
history/internal_docs/goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
history/internal_docs/call_for_review_goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
tests/goal5431_water_bg_outbox_refresh_test.py
```

Goal5432:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5432_public_artifact_live_refresh.json
history/internal_docs/goal5432_xhd_public_artifact_live_refresh_2026-07-10.md
history/internal_docs/call_for_review_goal5432_xhd_public_artifact_live_refresh_2026-07-10.md
tests/goal5432_public_artifact_live_refresh_test.py
```

Important source context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
```

## Summary To Attack

The packet claims:

```text
Goal5428 current matrix = 6 cases / 9 route results.
Full X-HD paper reproduction is still blocked by exact input artifacts or explicit exact-equivalence acceptance.
More route/performance work is not the next paper-reproduction step.
WaterBodies->BlockGroups is the strongest current exact-equivalence candidate.
Goal5430 makes that candidate actionable by preparing evidence and request material.
Goal5431 writes send-ready drafts, but they are not sent.
Goal5432 refreshes public artifact surfaces and finds no new public exact-input path.
```

## Water/BG Evidence Under Review

Case:

```text
paper_pair = USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
author paper-config num_points_cell = 8
author paper-config HDResult = 0.8964367508888245
author matches paper log = true
RTDL exact-witness HDResult float64 = 0.8964380566690101
abs diff = 1.305780185645311e-06 <= 2e-6
per_source_witness_exact = true
```

Public reconstruction hashes:

```text
WaterBodies generated WKT sha256 =
0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39

BlockGroups generated WKT sha256 =
8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

Still not exact:

```text
No author WKT file hashes.
No proof current ArcGIS services are the author's exact snapshot.
No byte-identical regeneration proof.
Remaining point-count deltas are nonzero.
```

Not sufficient for exact status:

```text
matching point counts
matching MBRs
matching HDResult
matching author rerun on current public service snapshot
checked-in author logs
public repository source code without input hashes
```

## Outbox State

Goal5431 drafts:

```text
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
```

Both must remain:

```text
Status: prepared_not_sent
```

The author request asks for:

```text
USADetailedWaterBodies.wkt bytes or sha256 from the paper-run HDDatasets tree.
USACensusBlockGroupBoundaries.wkt bytes or sha256 from the paper-run HDDatasets tree.
Exact source URLs, snapshot dates, export parameters, and conversion scripts if files cannot be shared.
Paper-log command/config confirming num_points_cell=8.
Preprocessing / simplification / precision / coordinate / ring-vertex extraction policy.
```

The external review draft asks whether Water/BG can be accepted as
exact-equivalent under a renamed bounded public-reconstruction claim.  Default:

```text
bounded_public_reconstruction_only_keep_level_b
```

## Public Artifact Refresh State

Goal5432 live refresh:

```text
ACM supplement URLs for ics26-106.zip
Crossref DOI metadata for 10.1145/3797905.3800509
GitHub repo metadata / releases / contents / recursive tree for pwrliang/X-HD
Rubao Lee public PDF URL
Liang Geng publication page URL
```

Observed:

```text
new_public_exact_input_artifact_found = false
acm_supplement_inspected = false
external_artifacts_acquired = false
exact_input_blocker_removed = false
```

ACM:

```text
HEAD / ranged GET checks = 403
zip_magic_observed = false
```

Crossref:

```text
dataset_or_artifact_link_found = false
```

GitHub:

```text
release_count = 0
root_data_directory_found = false
dataset_archive_release_found = false
tree_likely_input_dataset_blob_found = false
```

The recursive GitHub tree has checked-in logs whose filenames contain `.wkt` /
`.nii` input names.  These are not input datasets, not paper input hashes, not a
release asset, and not an HDDatasets bundle.

## Claim Boundary To Attack

Authorized:

```text
decision_refresh_claimed
packet_claimed
author_artifact_request_prepared
exact_equivalence_review_packet_prepared
outbox_refreshed
public_artifact_refresh_claimed
```

Forbidden:

```text
request_sent_claimed
external_artifacts_acquired
exact_equivalence_accepted
new_public_exact_input_artifact_found
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

This packet mentions hashes, byte identity, explicit `-lb`, and row/hash work
only as blockers or stopped lines. It must not be app-artifact parity
implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: exact-input / exact-equivalence decision packet, author artifact request, public artifact availability refresh
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Expected G-1 interpretation:

```text
PASS: provenance / review / request packet; no row/hash/offload-stream implementation work.
```

## Validation Evidence Already Run

Goal5429:

```text
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5429_xhd_exact_input_or_equivalence_decision_refresh_2026-07-10.md
py -m unittest tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5427_water_bg_paper_config_consolidation_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

Goal5430:

```text
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
py -m unittest tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

Goal5431:

```text
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md history/internal_docs/call_for_review_goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
py -m unittest tests.goal5431_water_bg_outbox_refresh_test tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Goal5432:

```text
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5432_xhd_public_artifact_live_refresh_2026-07-10.md history/internal_docs/call_for_review_goal5432_xhd_public_artifact_live_refresh_2026-07-10.md
py -m unittest tests.goal5432_public_artifact_live_refresh_test tests.goal5431_water_bg_outbox_refresh_test tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if commands exit successfully.

## Requested Verdict Labels

Approve:

```text
approve_goals5429_5432_xhd_exact_input_equivalence_blocker_packet
```

Revise:

```text
revise_goals5429_5432_xhd_exact_input_equivalence_blocker_packet
```

Block:

```text
block_goals5429_5432_xhd_exact_input_equivalence_blocker_packet
```

## Review Questions

1. Does Goal5429 correctly identify exact input artifacts or explicit
   exact-equivalence acceptance as the current blocker?
2. Is it correct to reject more route micro-optimization and explicit `-lb`
   work as the next paper-reproduction step?
3. Is WaterBodies->BlockGroups correctly identified as the strongest current
   exact-equivalence candidate without self-promoting it to exact?
4. Does Goal5430 package the evidence honestly, including both pro-acceptance
   and anti-acceptance facts?
5. Does the author request ask for the right WKT bytes/hashes or regeneration
   provenance?
6. Does the exact-equivalence request correctly default to Level-B unless
   acceptance is explicit?
7. Does Goal5431 keep both outbox drafts `prepared_not_sent` and avoid implying
   the requests were sent?
8. Does Goal5432 perform real live checks, and does its evidence support
   "no new public exact-input path found"?
9. Is the ACM supplement correctly treated as visible but uninspected because
   zip bytes were not downloaded?
10. Does the packet correctly distinguish author logs / GitHub log filenames
    from actual input dataset artifacts or hashes?
11. Does the packet avoid exact paper, Figure 5, full paper, performance ratio,
    author RT-core equivalence, POD, route-code, and `-lb` claims?
12. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
    implementation?
13. Is it correct that POD is not expected until new artifacts, hashes,
    byte-identical regeneration, ACM supplement contents, or accepted
    exact-equivalence appears?
14. Is the next action correct: send/review the Goal5431 outbox or wait for
    external author/ACM/exact-equivalence response?
15. Are there any missing external surfaces that should be refreshed before
    declaring this blocker node ready for owner/external action?

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
15. ...
```
