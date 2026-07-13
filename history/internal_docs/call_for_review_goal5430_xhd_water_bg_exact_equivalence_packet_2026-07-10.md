# Call For Review - Goal5430 X-HD Water/BG Exact-Equivalence Packet

Please strictly review Goal5430.

This is a provenance / review / request packet.  It does **not** claim exact
paper input recovery, Figure 5 reproduction, full X-HD paper reproduction,
author RT-core equivalence, performance ratio, or route improvement.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5430_water_bg_exact_equivalence_packet.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
tests/goal5430_water_bg_exact_equivalence_packet_test.py
history/internal_docs/goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5429_exact_input_or_equivalence_decision_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md
scripts/xhd_stop_loss_gate_check.py
```

## Packet Summary

Goal5430 packages the strongest current WaterBodies->BlockGroups Level-B
evidence:

```text
paper_pair = USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
```

Author paper-config evidence:

```text
num_points_cell = 8
author HDResult = 0.8964367508888245
author matches paper log = true
author Running.AvgTime = 110.167 ms
```

RTDL evidence:

```text
RTDL exact-witness float64 = 0.8964380566690101
abs diff vs author = 1.305780185645311e-06
comparison tolerance = 2e-6
matched_with_declared_tolerance = true
per_source_witness_exact = true
same_witness_float32_distance = 0.8964367508888245
```

Public reconstruction evidence:

```text
WaterBodies sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
WaterBodies point delta = +6129
WaterBodies max_abs_mbr_delta = 2.9081737551450715e-06

BlockGroups sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
BlockGroups point delta = +127
BlockGroups max_abs_mbr_delta = 3.7103264247662082e-06
```

Why still not exact:

```text
No author WKT file hashes.
No proof that current ArcGIS services are the author's exact snapshot.
No byte-identical regeneration proof.
Remaining point-count deltas are nonzero.
```

## Author Artifact Request

Goal5430 prepares a request for:

```text
USADetailedWaterBodies.wkt bytes or sha256 from the paper-run HDDatasets tree
USACensusBlockGroupBoundaries.wkt bytes or sha256 from the paper-run HDDatasets tree
exact source URLs, snapshot dates, export parameters, and conversion scripts if files cannot be shared
paper-log command/config confirming num_points_cell=8
preprocessing / simplification / precision / coordinate / ring-vertex extraction policy
```

## External Exact-Equivalence Review Question

```text
Can the current deterministic public ArcGIS reconstruction be accepted as
exact-equivalent for a renamed bounded public-reconstruction claim, or must it
remain Level-B same-source evidence?
```

Default without explicit external acceptance:

```text
bounded_public_reconstruction_only_keep_level_b
```

## Claim Boundary To Attack

Authorized:

```text
packet_claimed
author_artifact_request_prepared
exact_equivalence_review_packet_prepared
```

Forbidden:

```text
exact_paper_dataset_reproduction_claimed
exact_equivalence_accepted_claimed
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

This goal mentions hashes / byte identity as provenance requests only.  It must
not be treated as row identity, hash parity, offload-stream, or app-artifact
implementation work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: author artifact/hash request and external exact-equivalence review packet; no app-artifact parity implementation
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5430_water_bg_exact_equivalence_packet.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5430_water_bg_exact_equivalence_packet.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
py -m unittest tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5430_xhd_water_bg_exact_equivalence_packet
```

Revise:

```text
revise_goal5430_xhd_water_bg_exact_equivalence_packet
```

Block:

```text
block_goal5430_xhd_water_bg_exact_equivalence_packet
```

## Review Questions

1. Does Goal5430 accurately package the WaterBodies->BlockGroups evidence
   without promoting it to exact paper input?
2. Are the public reconstruction hashes, point-count deltas, MBR deltas,
   author paper-config scalar, and RTDL scalar evidence correctly represented?
3. Is the author artifact/hash request specific enough to unlock exact input
   provenance if authors respond?
4. Is the exact-equivalence review question framed correctly, with
   `bounded_public_reconstruction_only_keep_level_b` as the default without
   explicit acceptance?
5. Does the packet correctly say that point counts, MBRs, and scalar HDResult
   are not sufficient to prove exact dataset identity?
6. Does the packet avoid claiming Figure 5, full paper reproduction,
   author-vs-RTDL ratio, or author RT-core equivalence?
7. Does the packet avoid route micro-optimization and new POD work?
8. Does the Stop-Loss G-1 answer pass, or does the packet secretly reopen
   app-artifact parity work?
9. Is the decision matrix correct for the four outcomes: author hashes,
   byte-identical regeneration, external acceptance, or stay Level-B?
10. Is the recommended next step correct: wait for external artifacts/review
    decision, then run same-input gates only if something changes?

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
