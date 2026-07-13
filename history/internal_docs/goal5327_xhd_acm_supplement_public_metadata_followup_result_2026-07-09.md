# Goal5327 - X-HD ACM Supplement Public Metadata Follow-up

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5327 follows up the unresolved ACM `ics26-106.zip` item from Goal5325.

It asks:

```text
Can public search, direct ACM supplement URLs, or Crossref DOI metadata reveal
an accessible X-HD artifact path, dataset mirror, or dataset/hash metadata
without needing ACM access or author response?
```

This is a narrow public-metadata follow-up. It does not run author `hd_exec`,
RTDL, POD, or performance comparisons.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5327_acm_supplement_public_metadata_followup.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5327.acm_supplement_public_metadata_followup.v1
```

## Evidence Checked

### Targeted Public Search

Queries:

```text
"ics26-106.zip"
"10.1145/3797905.3800509" "ics26-106.zip"
"X-HD" "ics26-106.zip"
"X-HD" "HDDatasets" "hd_exec"
"X-HD: Fast Hausdorff Distance Computation with Ray Tracing"
"Camera-Ready Submission" "Paper 106" "X-HD"
```

Result:

```text
The ACM proceedings/supplement listing is visible.
No public dataset mirror was found.
No author-hosted HDDatasets bundle was found.
No alternate downloadable supplement copy was found.
```

### ACM Supplement URL Checks

Checked:

```text
https://dl.acm.org/action/downloadSupplement?doi=10.1145%2F3797905.3800509&file=ics26-106.zip
https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip
```

Observed:

```text
HEAD -> 403
downloaded = false
```

### Crossref DOI Metadata

Checked:

```text
https://api.crossref.org/works/10.1145/3797905.3800509
```

Observed:

```text
title = X-HD: Fast Hausdorff Distance Computation with Ray Tracing
doi = 10.1145/3797905.3800509
link_count = 1
link = https://dl.acm.org/doi/abs/10.1145/3797905.3800509
relation_keys = []
archive = []
dataset_or_artifact_link_found = false
```

## Exit Label

```text
acm_supplement_still_unresolved__no_public_metadata_or_mirror_path_found
```

## Interpretation

Goal5327 strengthens Goal5325:

```text
The ACM supplement is still visible but not publicly downloadable from this
environment. Public metadata does not reveal a dataset/artifact mirror or
dataset hash path. The next required actor remains an ACM-access reviewer or
the paper authors.
```

It also strengthens Goal5326:

```text
The external request package is still needed.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5327_acm_supplement_public_metadata_followup.json
py -m unittest tests.goal5327_xhd_acm_supplement_public_metadata_followup_test
py -m unittest tests.goal5325_xhd_public_web_supplement_artifact_sweep_test tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test
```

Observed:

```text
Ran 6 tests OK
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
Goal5327 rechecked the ACM supplement and DOI metadata path. The supplement
remains visible but inaccessible from this environment, Crossref exposes only
the ACM article link, and no public mirror or dataset link was found.
```

Forbidden:

```text
claiming the ACM supplement has been inspected;
claiming the ACM supplement contains datasets;
claiming the ACM supplement contains no useful artifacts;
claiming all publication-adjacent artifacts are exhausted;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5327 did not use POD.

POD is not useful until an artifact, hash manifest, regeneration script, or
accepted public reconstruction exists and needs author/RTDL verification.
