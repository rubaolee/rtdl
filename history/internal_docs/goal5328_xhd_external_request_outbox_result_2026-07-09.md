# Goal5328 - X-HD External Request Outbox

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5328 turns the Goal5326 request package and Goal5327 ACM supplement
follow-up into a local, send-ready outbox.

It asks:

```text
Can the owner now copy/send concrete messages to the paper authors, an
ACM-access reviewer, or an exact-equivalence reviewer without relying on chat
history?
```

This goal prepares drafts only. It does not send them.

## New Files

Outbox directory:

```text
Paper-reproduction-apps/x-hd-paper/requests/
```

Files:

```text
Paper-reproduction-apps/x-hd-paper/requests/README.md
Paper-reproduction-apps/x-hd-paper/requests/author_input_provenance_request.md
Paper-reproduction-apps/x-hd-paper/requests/acm_supplement_inspection_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5328_external_request_outbox.json
```

## Contact Sources

Recorded public contact sources:

```text
X-HD paper PDF first page
Liang Geng publication page
```

The author request draft records public paper emails for:

```text
Liang Geng
Zhehu Yuan
Rubao Lee
Fusheng Wang
Xiaodong Zhang
```

## Outbox Messages

### Author Input Provenance Request

Asks for:

```text
paper HDDatasets file hashes;
input archive if redistributable;
byte-identical regeneration scripts;
graphics preprocessing/scaling parameters;
geo WKT files/hashes and conversion details;
BraTS validation file list/hashes and NIfTI-to-point rule;
missing command/config details.
```

### ACM Supplement Inspection Request

Asks an ACM-access reviewer to inspect:

```text
ics26-106.zip
```

and report:

```text
top-level listing;
whether it is manuscript-only or artifact material;
datasets/hashes/scripts/instructions if present;
zip sha256 if downloadable.
```

### WaterBodies/BG Exact-Equivalence Review Request

Asks for one of:

```text
accepted_as_exact_equivalent_with_named_boundary
accepted_only_as_level_b_public_reconstruction
rejected_keep_level_b
```

Default without explicit answer:

```text
rejected_keep_level_b
```

## Exit Label

```text
external_request_outbox_ready__await_owner_send
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5328_external_request_outbox.json
py -m unittest tests.goal5328_xhd_external_request_outbox_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test
```

Observed:

```text
Ran 7 tests OK
Ran 20 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5328 prepares local send-ready request drafts and public author contact
metadata.
```

Forbidden:

```text
claiming the author request has been sent;
claiming any recipient has responded;
claiming external artifacts have been acquired;
claiming ACM supplement contents are known;
claiming exact-equivalence has been accepted;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5328 did not use POD.

POD becomes relevant only after a positive external response provides artifacts,
hashes, regeneration instructions, or accepted reconstruction criteria.
