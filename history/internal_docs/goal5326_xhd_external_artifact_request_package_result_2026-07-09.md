# Goal5326 - X-HD External Artifact Request Package

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5326 turns the exact-input blocker from Goals5318-5325 into a concrete
external request package.

Current X-HD full-paper reproduction status:

```text
Level-B public/source-matched evidence is strong.
Exact paper input files/hashes are not available.
Full paper reproduction is not complete.
More route/performance work is not the next paper-reproduction step.
```

This goal prepares request text and response-handling rules for:

```text
paper authors;
ACM-access reviewer for the unresolved `ics26-106.zip` supplement;
owner / external reviewer exact-equivalence decision.
```

It does not send any request and does not acquire any new artifact.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5326_external_artifact_request_package.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5326.external_artifact_request_package.v1
```

Status:

```text
external_artifact_request_package_ready__not_sent_by_codex
```

## Request Targets

### Paper Authors

The package asks the authors for any of:

```text
sha256 manifest for paper-run /local/storage/shared/HDDatasets inputs;
input files or archive if redistributable;
converted point-set hashes if raw data cannot be shared;
preprocessing/conversion scripts and parameters;
paper command-line/config options not captured by checked-in logs.
```

The request explicitly covers:

```text
graphics: Dragon / HappyBuddha / AsianDragon / ThaiStatuette;
geo: dtl_cnty / uszipcode / USADetailedWaterBodies /
     USACensusBlockGroupBoundaries / lakes / parks / all_nodes;
BraTS: validation file list/hashes and NIfTI-to-point conversion rule.
```

### ACM-Access Reviewer

The package asks a reviewer with ACM access to inspect:

```text
ics26-106.zip
```

and report:

```text
top-level file listing;
README or artifact appendix if present;
presence/absence of data files, hashes, scripts, or dataset instructions;
zip sha256 if downloadable.
```

This directly follows Goal5325: direct access from this environment returned
HTTP 403, so the item remains unresolved.

### Owner / External Review

If author artifacts are unavailable, the package asks whether the current
WaterBodies/BG full-public reconstruction may be accepted under a renamed
bounded exact-equivalence claim.

Default without an explicit answer:

```text
rejected_keep_level_b
```

## Response Handling

Positive response types sufficient to continue:

```text
author_hash_manifest;
author_input_archive;
byte_identical_regeneration_script;
acm_supplement_contains_artifact_instructions_or_hashes.
```

Negative or insufficient response:

```text
explicit_non_availability_statement
```

That response is useful for status, but does not unblock full paper
reproduction. It keeps the line at Level-B unless an exact-equivalence review
accepts a renamed bounded claim.

## Exit Label

```text
external_artifact_request_package_ready__await_owner_send_or_external_response
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5326_external_artifact_request_package.json
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test
py -m unittest tests.goal5324_xhd_exact_input_acquisition_packet_test tests.goal5325_xhd_public_web_supplement_artifact_sweep_test tests.goal5326_xhd_external_artifact_request_package_test
```

Observed:

```text
Ran 7 tests OK
Ran 21 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5326 prepares concrete author, ACM-access, and exact-equivalence request
text plus response-handling rules.
```

Forbidden:

```text
claiming the author request has been sent by Codex;
claiming external artifacts have been acquired;
claiming ACM supplement contents are known;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5326 did not use POD.

POD is not expected until a positive response supplies inputs, hashes,
regeneration instructions, or an externally accepted public reconstruction that
needs author `hd_exec` or RTDL verification.
