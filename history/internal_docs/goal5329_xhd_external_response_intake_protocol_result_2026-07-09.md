# Goal5329 - X-HD External Response Intake Protocol

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5329 defines how future author, ACM-access, or exact-equivalence responses
should be normalized, validated, and mapped to the next X-HD reproduction
action.

This follows Goal5328: we now have send-ready outbox drafts, but no request has
been sent by Codex and no external response has arrived.

Goal5329 prevents the next response from being interpreted ad hoc in chat.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
Paper-reproduction-apps/x-hd-paper/requests/incoming/README.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5329_external_response_intake_protocol.json
tests/goal5329_xhd_external_response_intake_protocol_test.py
```

## Supported Response Types

```text
author_hash_manifest
author_input_archive
byte_identical_regeneration_script
acm_supplement_artifact_instructions
exact_equivalence_verdict
explicit_non_availability_statement
other
```

Each response type records:

```text
minimum fields;
whether it is sufficient to run a POD gate;
whether it is sufficient to claim exact input.
```

Default posture:

```text
fail closed
```

## Intake Rules

Examples:

```text
verified author input bytes or archive
  -> create provenance-ingestion goal, record hashes, run smallest author/RTDL
     same-input gate on POD.

hashes but no bytes
  -> compare against local/public candidates if possible; request missing bytes
     or regeneration path if no match.

byte-identical regeneration procedure
  -> regenerate, record output hashes, then run same-input gates.

ACM supplement artifact instructions
  -> ingest supplement listing/instructions and map to paper workloads before
     route execution.

WaterBodies/BG exact-equivalence accepted
  -> run the accepted bounded matrix under the accepted claim name, not stronger
     wording.

rejection / no artifacts
  -> keep full-paper claims blocked and stop at Level-B for that scope.
```

## Privacy Boundary

Goal5329 adds a repository hygiene rule:

```text
Raw private messages should not be committed.
```

Allowed repository record:

```text
minimal metadata;
hashes;
permissions;
claim boundary;
next-action classification.
```

Raw response content should only be committed if the sender explicitly allows
it.

## Exit Label

```text
external_response_intake_protocol_ready__await_response
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5329_external_response_intake_protocol.json
py -m json.tool Paper-reproduction-apps\x-hd-paper\requests\external_response_intake_template.json
py -m unittest tests.goal5329_xhd_external_response_intake_protocol_test
py -m unittest tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Observed:

```text
Ran 7 tests OK
Ran 14 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5329 defines how future author, ACM, or exact-equivalence responses will be
normalized and mapped to next actions.
```

Forbidden:

```text
claiming a response has arrived;
claiming external artifacts have been acquired;
claiming ACM supplement has been inspected;
claiming exact-equivalence has been accepted;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5329 did not use POD.

POD becomes relevant only after a concrete positive response supplies artifacts,
regeneration instructions, or accepted reconstruction criteria.
