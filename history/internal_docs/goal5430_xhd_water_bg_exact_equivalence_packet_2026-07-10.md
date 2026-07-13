# Goal5430 - X-HD Water/BG Exact-Equivalence Review Packet And Author Artifact Request

## Verdict

```text
water_bg_exact_equivalence_packet_ready__await_external_decision_or_author_artifacts
```

Goal5430 turns the strongest current WaterBodies->BlockGroups Level-B evidence
into an actionable exact-equivalence review packet and author artifact/hash
request.

This is an evidence/request packet.  It performs no POD execution, no author
execution, no RTDL execution, no route optimization, and no claim promotion.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5430.water_bg_exact_equivalence_packet.v1
status = water_bg_exact_equivalence_packet_ready__await_external_decision_or_author_artifacts
recommended_next_goal = Goal5431_wait_for_external_artifacts_or_review_decision_then_run_same_input_gate_if_available
```

## Source Decision

Goal5430 follows Goal5429:

```text
from_goal5429 = exact_input_artifacts_or_explicit_exact_equivalence_acceptance
route_micro_optimization_authorized = false
explicit_lb_authorized = false
pod_expected_now = false
```

## Case

```text
case_id = geo_water_bg_full_public_paper_config
paper_pair = USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
paper_log_path_root = /local/storage/shared/HDDatasets
```

Paper-config author evidence:

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
route_sec = 61.562113016843796
entrypoint_total_sec = 873.2409668043256
```

## Public Reconstruction Evidence

WaterBodies:

```text
service_item_id = 48c77cbde9a0470fb371f8c8a8a7421a
service_url = https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Water_Bodies/FeatureServer
generated_wkt_sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
generated_wkt_bytes = 741925630
generated_author_loader_point_count = 22824823
paper_point_count = 22818694
point_count_delta = 6129
point_count_relative_delta = 0.0002685955646716679
max_abs_mbr_delta = 2.9081737551450715e-06
```

BlockGroups:

```text
service_item_id = 2f5e592494d243b0aa5c253e75e792a4
service_url = https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_BlockGroups/FeatureServer
generated_wkt_sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
generated_wkt_bytes = 1560257609
generated_author_loader_point_count = 52271467
paper_point_count = 52271340
point_count_delta = 127
point_count_relative_delta = 2.4296296976507585e-06
max_abs_mbr_delta = 3.7103264247662082e-06
```

Summary:

```text
mbrs_match_paper_logs_with_small_delta = true
author_paper_config_value_reproduced = true
rtdl_matches_author_with_tolerance = true
still_not_exact = true
```

## Why This Is Still Not Exact

```text
No author WKT file hashes.
No proof that current ArcGIS services are the author's exact snapshot.
No byte-identical regeneration proof.
Remaining point-count deltas are nonzero.
```

## Author Artifact / Hash Request

Prepared request items:

```text
USADetailedWaterBodies.wkt bytes or sha256 from the paper-run HDDatasets tree.
USACensusBlockGroupBoundaries.wkt bytes or sha256 from the paper-run HDDatasets tree.
If files cannot be shared, exact source URLs, snapshot dates, export parameters, and conversion scripts sufficient to regenerate the paper-run WKT files.
The exact command line or config for the paper-log run confirming num_points_cell=8 for this pair.
Any preprocessing, simplification, precision, coordinate, or ring/vertex extraction policy used to produce the paper-run WKT inputs.
```

Prepared message:

```text
We are reproducing the X-HD WaterBodies->BlockGroups case. Our public ArcGIS
reconstruction matches the paper-log scalar under the author paper config and
RTDL matches the author rerun, but we cannot claim exact paper reproduction
without the paper-run WKT files, hashes, or byte-identical regeneration
details. Could you provide sha256 hashes or sufficient regeneration provenance
for USADetailedWaterBodies.wkt and USACensusBlockGroupBoundaries.wkt?
```

## External Exact-Equivalence Review Packet

Question:

```text
Can the current deterministic public ArcGIS reconstruction be accepted as
exact-equivalent for a renamed bounded public-reconstruction claim, or must it
remain Level-B same-source evidence?
```

Evidence for acceptance:

```text
Both services are public ArcGIS sources matching the paper pair names.
WaterBodies and BlockGroups MBR deltas are under 1e-5 degrees.
Point-count deltas are small relative to paper logs: +6129 WaterBodies and +127 BlockGroups.
Author hd_exec with paper-config n_points_cell=8 reproduces the paper-log HDResult.
RTDL exact-witness route matches the author paper-config rerun within 2e-6.
Generated WKT sha256 values are recorded.
```

Evidence against acceptance:

```text
No author-provided WKT file hashes are available.
No proof current ArcGIS services are the author's exact snapshot.
No byte-identical regeneration proof exists.
Point-count deltas are nonzero.
Statistics and scalar agreement do not prove byte identity.
```

Allowed review outcomes:

```text
exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim
bounded_public_reconstruction_only_keep_level_b
not_accepted_keep_level_b
```

Default without external acceptance:

```text
bounded_public_reconstruction_only_keep_level_b
```

## Decision Matrix

```text
author WKT files or sha256 hashes acquired
  -> run same-input author/RTDL verification and build denominator-aligned matrix

byte-identical regeneration path acquired
  -> regenerate, record sha256, then run same-input author/RTDL verification

external exact-equivalence accepted
  -> rename claim exactly and run bounded public-reconstruction matrix under accepted scope

no artifacts and no exact-equivalence acceptance
  -> keep Water/BG at Level-B and do not claim Figure 5 or full paper reproduction
```

## Claim Boundary

Authorized:

```text
packet_claimed = true
author_artifact_request_prepared = true
exact_equivalence_review_packet_prepared = true
```

Not authorized:

```text
exact_paper_dataset_reproduction_claimed = false
exact_equivalence_accepted_claimed = false
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

This goal mentions hashes and byte identity only as provenance requirements.
It does not start row identity, hash parity, offload stream, or other app
artifact implementation work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: author artifact/hash request and external exact-equivalence review packet; no app-artifact parity implementation
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: this is a provenance/review packet, not row/hash/offload-stream implementation work.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5430_water_bg_exact_equivalence_packet.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5430_water_bg_exact_equivalence_packet.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
py -m unittest tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5324_xhd_exact_input_acquisition_packet_test
```

The known Windows Python prefix warning may appear and is not a failure if
tests pass.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5430_water_bg_exact_equivalence_packet.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
tests/goal5430_water_bg_exact_equivalence_packet_test.py
history/internal_docs/goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
history/internal_docs/call_for_review_goal5430_xhd_water_bg_exact_equivalence_packet_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5431_wait_for_external_artifacts_or_review_decision_then_run_same_input_gate_if_available
```

Goal5431 should not run POD unless one of these appears:

```text
author WKT files/hashes
byte-identical regeneration path
external exact-equivalence acceptance
```
