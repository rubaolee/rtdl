# X-HD WaterBodies/BG External Action Packet

Status: `prepared_not_sent`

This packet is the single entry point for the next X-HD
WaterBodies->BlockGroups external action. It packages what to send, how
to normalize any response, how to classify the response, and what is
still forbidden.

## Current State

```text
case_id = geo_water_bg_full_public_paper_config
paper_pair = USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
author paper-config num_points_cell = 8
author paper-config HDResult = 0.8964367508888245
RTDL exact-witness HDResult = 0.8964380566690101
abs diff = 1.305780185645311e-06 <= 2e-06
per_source_witness_exact = true
```

This is strong Level-B public-reconstruction evidence. It is **not** exact
paper input reproduction.

## Current Public Reconstruction Hashes

```text
USADetailedWaterBodies.wkt =
0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39

USACensusBlockGroupBoundaries.wkt =
8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

WaterBodies details:

```text
service_item_id = 48c77cbde9a0470fb371f8c8a8a7421a
service_url = https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Water_Bodies/FeatureServer
point_count_delta = 6129
max_abs_mbr_delta = 2.9081737551450715e-06
```

BlockGroups details:

```text
service_item_id = 2f5e592494d243b0aa5c253e75e792a4
service_url = https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_BlockGroups/FeatureServer
point_count_delta = 127
max_abs_mbr_delta = 3.7103264247662082e-06
```

## Public Artifact Refresh

Goal5432 status:

```text
public_artifact_refresh_no_new_exact_input_path__acm_supplement_still_uninspected
new_public_exact_input_artifact_found = false
acm_supplement_inspected = false
exact_input_blocker_removed = false
```

Interpretation:

```text
No public exact input path is currently known.
ACM supplement bytes were not downloaded, so the supplement is not
inspected.
```

## What To Send Or Review

Author/artifact-owner request:

```text
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
```

Exact-equivalence review request:

```text
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
```

Both drafts are `prepared_not_sent`. Sending is an owner/external action,
not a claim that a response exists.

## If A Response Arrives

1. Save a normalized metadata record with:

```text
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
```

2. If the response contains private material, store only minimal metadata
in the repository unless the sender permits committing raw text.

3. Classify it:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py --input <response.json> --output <classified.json>
```

4. Follow the classifier `recommended_next_action`. Do not improvise a
stronger claim.

## Positive Classifications

```text
author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim
author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate
byte_identical_regeneration_available__run_regeneration_then_hash_gate
acm_supplement_contains_possible_provenance__map_before_route
exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix
```

Even these positive classifications do **not** directly authorize exact
paper reproduction wording. They authorize the next gate.

## Fail-Closed Cases

Keep Level-B if:

```text
one of the required WKT paths is missing
hashes do not match current public reconstruction
response type is unknown or underspecified
exact-equivalence verdict is not Water/BG scoped
exact-equivalence verdict lacks an accepted claim name
response says artifacts are unavailable
```

## Claim Boundary

Authorized:

```text
external_action_packet_prepared = true
```

Not authorized:

```text
request_sent_claimed = false
external_response_received = false
external_artifacts_acquired = false
exact_equivalence_accepted = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
pod_execution_claimed = false
new_rtdl_route_code_added = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Rule

This packet does not reopen row/hash/offload-stream implementation work.
It only packages external action and response classification.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external action packet / response classification workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```
