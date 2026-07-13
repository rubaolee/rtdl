# Goal5339 - X-HD Mapped-Candidate Same-Input Gate Packet

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5339 adds an app-owned command-packet builder for a future mapped-candidate
same-input POD gate.

It follows Goal5338. Goal5338 validates that hashed candidate files are mapped
to known paper workload roles. Goal5339 turns an accepted clean mapping plus
materialized candidate files into author `hd_exec` and RTDL `hd_exec`-compatible
command plans.

It does not execute the commands, run POD, compare author/RTDL outputs, or
claim exact paper reproduction.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_mapped_candidate_same_input_gate_packet.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5339_mapped_candidate_same_input_gate_packet.json
tests/goal5339_xhd_mapped_candidate_same_input_packet_test.py
```

## Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_mapped_candidate_same_input_gate_packet.py <mapping_review_json> --materialized-root <candidate_root> --output-dir <pod_output_dir> [--author-bin <hd_exec>] [--rtdl-route <route>] [--output <packet_json>]
```

Input schema:

```text
rtdl.paper_reproduction.xhd.candidate_workload_mapping_review.v1
```

Output schema:

```text
rtdl.paper_reproduction.xhd.mapped_candidate_same_input_gate_packet.v1
```

The packet contains:

```text
workload_id;
paper figure label;
direction;
n_dims;
input_type;
materialized input paths;
author hd_exec command;
RTDL hd_exec-compatible command;
expected output JSON paths;
claim boundaries.
```

## Classification

Statuses:

```text
mapped_candidate_same_input_gate_commands_ready
accepted_mapping_but_candidate_files_not_materialized
mapping_review_not_ready_for_same_input_gate
```

Only `mapped_candidate_same_input_gate_commands_ready` can feed a later POD
execution goal.

## Validated Behaviors

Tests cover:

```text
accepted mapping plus materialized files builds author and RTDL command plans;
accepted mapping without materialized files is not POD-ready;
proposed mapping is not command-ready;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5339_mapped_candidate_same_input_gate_packet.json
py -m unittest tests.goal5339_xhd_mapped_candidate_same_input_packet_test
py -m unittest tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test
```

Observed:

```text
json.tool OK
Ran 4 tests OK
Ran 9 tests OK
Ran 75 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5339 adds an app-owned command-packet builder for a future mapped-candidate
same-input POD gate. It does not execute commands and does not claim
reproduction.
```

Forbidden:

```text
claiming commands were executed by this packet;
claiming same-input correctness from this packet alone;
claiming exact paper dataset reproduction from this packet alone;
claiming Figure 5 reproduction from this packet alone;
claiming full X-HD paper reproduction from this packet alone;
claiming author-vs-RTDL performance ratio from this packet alone;
running POD without scripts/current_pod_ssh.py.
```

## POD Use

Goal5339 did not use POD.

The generated command plans are for a later goal. That later goal must stage
real mapped candidate files, use `scripts/current_pod_ssh.py`, execute author
and RTDL commands, compare `HDResult`, and keep performance denominators
separate.

## Exit Label

```text
mapped_candidate_same_input_gate_packet_ready__await_real_accepted_mapping_and_files
```
