# Goal5341 - X-HD ACM Supplement Live Access Probe Result

Date: 2026-07-09

Status: `implemented_review_pending`

Exit label: `acm_supplement_live_access_probe_ready__current_environment_still_not_exact_input`

## Purpose

Goal5341 adds a reusable live-access probe for the unresolved ACM
`ics26-106.zip` supplement identified in Goals5325, 5327, and 5334.

The probe checks known ACM supplement URLs with `HEAD` and range `GET` requests,
records status codes and zip-magic evidence, and supports an optional cookie
file for future authorized ACM access.

This is still a provenance/access goal. It does not inspect zip contents, run
POD, run author `hd_exec`, run RTDL, or claim reproduction.

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/probe_xhd_acm_supplement_live_access.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5341_acm_supplement_live_access_probe_live.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5341_acm_supplement_live_access_probe.json
tests/goal5341_xhd_acm_live_access_probe_test.py
```

## Live Probe Result

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\probe_xhd_acm_supplement_live_access.py --timeout-sec 20 --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5341_acm_supplement_live_access_probe_live.json
```

Observed classification:

```text
acm_supplement_visible_but_forbidden_from_current_environment
```

Observed URL behavior:

```text
https://dl.acm.org/action/downloadSupplement?doi=10.1145%2F3797905.3800509&file=ics26-106.zip
  HEAD 403
  range GET 403
  content-type text/html; charset=UTF-8
  zip magic false

https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip
  HEAD 403
  range GET 403
  content-type text/html; charset=UTF-8
  zip magic false

https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=true
  HEAD 403
  range GET 403
  content-type text/html; charset=UTF-8
  zip magic false
```

Interpretation:

```text
The current unauthenticated environment still cannot download the ACM
supplement. The response is forbidden HTML, not zip bytes. The ACM supplement
remains visible but uninspected.
```

## Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5341_acm_supplement_live_access_probe_live.json
json.tool OK
```

Additional validation is provided by the Goal5341 focused test and the
Goal5326-Goal5341 chain test.

Observed:

```text
py -m unittest tests.goal5341_xhd_acm_live_access_probe_test
Ran 3 tests OK

py -m unittest tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test
Ran 8 tests OK

py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test
Ran 83 tests OK
```

## Claim Boundary

Allowed:

```text
Goal5341 adds a reusable ACM supplement live-access probe.
The current unauthenticated environment still receives 403 HTML responses from
the known ACM supplement URLs.
No zip magic was observed.
The ACM supplement remains uninspected.
```

Not allowed:

```text
claiming the ACM supplement contents were inspected
claiming the ACM supplement contains datasets
claiming the ACM supplement contains no useful artifacts
claiming exact paper dataset reproduction
claiming Figure 5 reproduction
claiming full X-HD paper reproduction
claiming author-vs-RTDL performance ratio
running POD from this live-access probe
```

## Next Step

If an ACM-authorized user or author provides access:

```text
1. run probe_xhd_acm_supplement_live_access.py with a cookie file or downloaded zip;
2. run inspect_xhd_acm_supplement_zip.py;
3. run ingest_xhd_acm_artifact_instructions.py;
4. run map_xhd_acm_candidate_bytes_hashes.py;
5. run review_xhd_candidate_workload_mapping.py;
6. if accepted, run build_xhd_mapped_candidate_same_input_gate_packet.py;
7. only then execute author/RTDL commands on POD and compare with Goal5340.
```

Until then, the exact-input blocker remains active.
