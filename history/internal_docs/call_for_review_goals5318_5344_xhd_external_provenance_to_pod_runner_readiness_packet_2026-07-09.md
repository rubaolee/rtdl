# Call For Review: Goals5318-5344 X-HD External Provenance To POD-Runner Readiness Packet

Please strictly review the X-HD external provenance and mapped same-input
readiness packet from Goal5318 through Goal5344.

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
Goal5341 - ACM supplement live-access probe
Goal5342 - ACM artifact-to-packet local pipeline
Goal5343 - Mapped-candidate POD execution-plan builder
Goal5344 - Mapped-candidate POD execution-plan runner
```

## Current Positive-Evidence Path

```text
real ACM zip or author artifact appears
-> live access probe confirms zip bytes or authorized access path
-> local artifact-to-packet pipeline
   -> inspect zip/listing
   -> hash candidate bytes
   -> review workload mapping
   -> materialize candidate files
   -> build Goal5339 command packet
-> build Goal5343 POD execution plan
-> dry-run Goal5344 runner for stage audit
-> in a later explicit execution goal:
   -> run Goal5344 with --execute
   -> preflight/upload/remote-execute/download through scripts/current_pod_ssh.py
   -> local Goal5340 comparator
```

## Current Evidence

```text
ACM supplement remains visible but forbidden in the current unauthenticated environment;
zip contents have not been inspected;
Goal5342 has not processed the real ACM zip;
Goal5343 has not built a real command-ready POD plan;
Goal5344 has not executed POD operations;
Goal5340 has not compared real outputs;
no exact paper input reproduction / Figure 5 reproduction / full paper reproduction / performance ratio is authorized.
```

## Latest Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5344_mapped_candidate_pod_execution_runner.json
json.tool OK

py -m unittest tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test
Ran 3 tests OK

py -m unittest tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test
Ran 6 tests OK

py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test
Ran 92 tests OK
```

## Review Questions

1. Does the packet correctly preserve the exact-input blocker?
2. Is the ACM live-access probe useful and properly scoped?
3. Is the local artifact-to-packet orchestrator useful and properly scoped?
4. Is the POD execution-plan builder useful and properly scoped?
5. Is the dry-run-by-default POD execution runner useful and properly scoped?
6. Does Goal5344 correctly require `--execute` before any real POD or comparator
   work?
7. Does the packet correctly separate local readiness, POD planning, POD
   execution, output comparison, exact-input claims, and performance claims?
8. Are all invalid/proposed/missing-file/missing-output/access-forbidden/not
   command-ready/not-ready-plan cases fail-closed?
9. Is it correct that no POD execution evidence exists in this packet?
10. Are public-web/ACM/Crossref/GitHub refresh findings represented without
    overclaiming?
11. Are external response validation and ingestion protocols sufficient for
    future author/reviewer responses?
12. Are the claim boundaries complete?
13. Is it correct that no full X-HD paper reproduction / Figure 5 reproduction /
    author-vs-RTDL ratio is currently authorized?
14. Are Goals5318-5344 ready to close as an external-provenance-to-POD-runner
    readiness packet, while keeping full reproduction blocked pending exact
    inputs or a real mapped same-input POD execution?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5344_xhd_external_provenance_to_pod_runner_packet
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
