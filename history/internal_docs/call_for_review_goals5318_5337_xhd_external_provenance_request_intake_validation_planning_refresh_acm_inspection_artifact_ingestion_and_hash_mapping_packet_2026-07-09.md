# Call For Review: Goals5318-5337 X-HD External Provenance / ACM Artifact Packet

Please strictly review the X-HD external provenance packet from Goal5318
through Goal5337.

This packet exists because full X-HD paper reproduction still depends on exact
paper input provenance. It should be reviewed as an input-identity and
artifact-intake line, not as a performance line.

## Included Goals

```text
Goal5318 - Water/BG exact provenance search
Goal5319 - Graphics exact provenance search
Goal5320 - County/ZCTA source conversion investigation
Goal5321 - OSM lakes/parks all-nodes provenance search
Goal5322 - BraTS2020 access/conversion provenance
Goal5323 - External author/artifact availability sweep
Goal5324 - Exact input acquisition/equivalence decision packet
Goal5325 - Public web/supplement artifact sweep
Goal5326 - External artifact request package
Goal5327 - ACM supplement public metadata follow-up
Goal5328 - External request outbox
Goal5329 - External response intake protocol
Goal5330 - External response intake validator
Goal5331 - External response validation matrix
Goal5332 - External response ingest runner
Goal5333 - Provenance ingestion action planner
Goal5334 - Public artifact refresh
Goal5335 - ACM supplement zip inspector
Goal5336 - ACM artifact-instruction ingestion manifest
Goal5337 - ACM candidate bytes/hash mapping gate
```

## Latest Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_acm_candidate_bytes_hashes.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5334_public_artifact_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5335_acm_supplement_zip_inspector.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5336_acm_artifact_instruction_ingestion.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5337_acm_candidate_hash_mapping.json
tests/goal5335_xhd_acm_supplement_zip_inspector_test.py
tests/goal5336_xhd_acm_artifact_instruction_ingestion_test.py
tests/goal5337_xhd_acm_candidate_hash_mapping_test.py
```

Latest reports:

```text
history/internal_docs/goal5335_xhd_acm_supplement_zip_inspector_result_2026-07-09.md
history/internal_docs/goal5336_xhd_acm_artifact_instruction_ingestion_result_2026-07-09.md
history/internal_docs/goal5337_xhd_acm_candidate_hash_mapping_result_2026-07-09.md
```

## Current Packet Summary

The current evidence says:

```text
exact paper inputs are still not acquired;
public searches did not find a dataset/hash/regeneration package;
ACM ics26-106.zip is visible but inaccessible from this environment;
the project now has local tooling to inspect, ingest, classify, hash, and map
future ACM artifact contents if the zip is obtained;
no POD is authorized by synthetic examples or by unreviewed candidate entries.
```

## Latest Validation

Goal5337 validation:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5337_acm_candidate_hash_mapping.json
json.tool OK

py -m unittest tests.goal5337_xhd_acm_candidate_hash_mapping_test
Ran 5 tests OK

py -m unittest tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test
Ran 14 tests OK

py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test
Ran 66 tests OK
```

## Review Questions

1. Does the packet correctly preserve the exact-input blocker?
2. Are Goals5335-5337 the right local tools for future ACM supplement access?
3. Is it correct that candidate bytes plus matching hashes still require a
   workload mapping/review gate before POD?
4. Are all POD gates conservative and fail-closed?
5. Are public-web/ACM/Crossref/GitHub refresh findings represented without
   overclaiming?
6. Are external response validation and ingestion protocols sufficient for
   future author/reviewer responses?
7. Are the claim boundaries complete?
8. Is it correct that no full X-HD paper reproduction / Figure 5 reproduction /
   author-vs-RTDL ratio is currently authorized?
9. Are Goals5318-5337 ready to close as an external-provenance readiness packet,
   while keeping full reproduction blocked pending exact inputs?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5337_xhd_external_provenance_packet
or
Verdict: approve_with_required_amendments
or
Verdict: block_packet

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
9. ...
```
