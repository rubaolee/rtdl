# Call For Review: Goals5318-5340 X-HD External Provenance / Mapped Same-Input Readiness Packet

Please strictly review the X-HD external provenance readiness packet from
Goal5318 through Goal5340.

This packet is about exact-input provenance tooling and future same-input gate
readiness. It is not a performance packet and does not claim full X-HD paper
reproduction.

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
Goal5338 - Candidate workload mapping review gate
Goal5339 - Mapped-candidate same-input gate packet builder
Goal5340 - Mapped-candidate output comparator
```

## Latest Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_acm_candidate_bytes_hashes.py
Paper-reproduction-apps/x-hd-paper/scripts/review_xhd_candidate_workload_mapping.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_mapped_candidate_same_input_gate_packet.py
Paper-reproduction-apps/x-hd-paper/scripts/compare_xhd_mapped_candidate_same_input_outputs.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5335_acm_supplement_zip_inspector.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5336_acm_artifact_instruction_ingestion.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5337_acm_candidate_hash_mapping.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5338_candidate_workload_mapping_review.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5339_mapped_candidate_same_input_gate_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5340_mapped_candidate_output_comparison.json
tests/goal5335_xhd_acm_supplement_zip_inspector_test.py
tests/goal5336_xhd_acm_artifact_instruction_ingestion_test.py
tests/goal5337_xhd_acm_candidate_hash_mapping_test.py
tests/goal5338_xhd_candidate_workload_mapping_review_test.py
tests/goal5339_xhd_mapped_candidate_same_input_packet_test.py
tests/goal5340_xhd_mapped_candidate_output_comparator_test.py
```

Latest reports:

```text
history/internal_docs/goal5335_xhd_acm_supplement_zip_inspector_result_2026-07-09.md
history/internal_docs/goal5336_xhd_acm_artifact_instruction_ingestion_result_2026-07-09.md
history/internal_docs/goal5337_xhd_acm_candidate_hash_mapping_result_2026-07-09.md
history/internal_docs/goal5338_xhd_candidate_workload_mapping_review_result_2026-07-09.md
history/internal_docs/goal5339_xhd_mapped_candidate_same_input_gate_packet_result_2026-07-09.md
history/internal_docs/goal5340_xhd_mapped_candidate_output_comparator_result_2026-07-09.md
```

## Current Packet Summary

The packet now supports this future positive-evidence path:

```text
real ACM zip or author artifact appears
-> inspect zip/listing
-> classify artifact-like entries
-> parse candidate bytes and hash manifests
-> map hashed candidate files to known paper workload roles
-> if accepted, build author/RTDL command packet
-> in a later POD goal, execute the packet using scripts/current_pod_ssh.py
-> compare author/RTDL JSON outputs with Goal5340
```

The current evidence still says:

```text
exact paper inputs are not acquired;
ACM ics26-106.zip is visible but inaccessible from this environment;
synthetic tests do not inspect the real ACM zip;
Goal5339 has not executed commands;
Goal5340 has not compared real POD outputs;
no Figure 5/full-paper/performance-ratio claim is authorized.
```

## Latest Validation

Goal5340 validation:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5340_mapped_candidate_output_comparison.json
json.tool OK

py -m unittest tests.goal5340_xhd_mapped_candidate_output_comparator_test
Ran 5 tests OK

py -m unittest tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test
Ran 9 tests OK
```

Latest chain validation through Goal5339:

```text
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test
Ran 75 tests OK
```

## Review Questions

1. Does the packet correctly preserve the exact-input blocker?
2. Are Goals5335-5340 the right local tools for future ACM supplement access
   and mapped same-input execution?
3. Is it correct that candidate bytes plus matching hashes still require
   workload mapping/review before POD?
4. Is it correct that accepted clean workload mapping plus materialized files
   builds only a later POD command packet, not a completed gate?
5. Is it correct that Goal5340 is a post-execution comparator and not an
   executor?
6. Are all invalid/proposed/missing-file/missing-output cases fail-closed?
7. Are author and RTDL command templates appropriate for a later same-input POD
   gate?
8. Does Goal5340 compare `HDResult` with explicit tolerance while keeping
   author and RTDL timing fields separated?
9. Is it correct that the packet reports no author-vs-RTDL performance ratio?
10. Are public-web/ACM/Crossref/GitHub refresh findings represented without
    overclaiming?
11. Are external response validation and ingestion protocols sufficient for
    future author/reviewer responses?
12. Are the claim boundaries complete?
13. Is it correct that no full X-HD paper reproduction / Figure 5 reproduction /
    author-vs-RTDL ratio is currently authorized?
14. Are Goals5318-5340 ready to close as an external-provenance readiness
    packet, while keeping full reproduction blocked pending exact inputs or a
    real mapped same-input POD execution?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5340_xhd_external_provenance_packet
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
14. ...
```
