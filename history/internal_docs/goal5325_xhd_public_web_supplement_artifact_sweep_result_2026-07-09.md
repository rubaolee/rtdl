# Goal5325 - X-HD Public Web / Supplement Artifact Sweep

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5325 expands the exact-input search beyond the author GitHub repository.
It asks:

```text
Do publication pages, public PDFs, DOI/ACM surfaces, author pages, NSF PAR,
ResearchGate, Zenodo/Figshare/OSF-style searches, or public mirrors expose the
missing X-HD exact input datasets or hashes?
```

This goal is a public web / artifact availability sweep. It does not run author
`hd_exec`, RTDL routes, POD code, or performance comparisons.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5325_public_web_supplement_artifact_sweep.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5325.public_web_supplement_artifact_sweep.v1
```

## Surfaces Checked

Checked surfaces:

```text
ACM DOI page
ACM proceedings supplementary listing
Rubao Lee public PDF
Liang Geng publication page
NSF Public Access record
ResearchGate publication page
Zenodo / Figshare / OSF targeted web searches
BraTS public mirrors
```

## Key Findings

No public exact input dataset artifact was found on:

```text
author/public paper pages;
Rubao Lee PDF;
Liang Geng publication page;
NSF PAR;
ResearchGate;
Zenodo/Figshare/OSF targeted searches;
BraTS mirrors.
```

The public PDF / paper text points to the source-code repository:

```text
https://github.com/pwrliang/X-HD
```

but Goal5323 already classifies that repository as source/scripts/logs only.

## Important Unresolved Artifact

The ACM proceedings search result exposes:

```text
ics26-106.zip
```

described in search results as:

```text
Camera-Ready Submission for ICS '26, Paper 106
```

Download/HEAD attempts from this environment returned 403:

```text
https://dl.acm.org/action/downloadSupplement?doi=10.1145%2F3797905.3800509&file=ics26-106.zip
https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip
https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=true
```

Therefore the correct status is:

```text
ACM supplement unresolved / requires access or confirmation
```

This must not be over-read either way:

```text
Do not claim it contains datasets without inspection.
Do not claim it contains no useful artifacts without inspection.
```

Visible labeling suggests a camera-ready manuscript submission rather than an
HDDatasets bundle, but that is not proof. It remains a concrete artifact to
inspect.

## BraTS Mirrors

Public or registration-gated BraTS data mirrors exist, including official CBICA
access pages and Kaggle-style mirrors. They do not close X-HD exact identity
because X-HD needs:

```text
author-selected validation files;
file hashes;
NIfTI-to-point conversion provenance;
converted point-set hashes or byte-identical regeneration proof.
```

## Exit Label

```text
public_web_exact_dataset_artifacts_not_found__acm_supplement_unresolved
```

## Interpretation

Current status:

```text
no_public_exact_dataset_found__one_acm_supplement_requires_access_or_confirmation
```

This means:

```text
No public exact input dataset was found by the web sweep.
The ACM supplementary zip is the only newly identified publication-adjacent
artifact that still requires inspection.
Full paper reproduction remains blocked.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5325_public_web_supplement_artifact_sweep.json
py -m unittest tests.goal5325_xhd_public_web_supplement_artifact_sweep_test
py -m unittest tests.goal5323_xhd_external_author_artifact_availability_test tests.goal5324_xhd_exact_input_acquisition_packet_test tests.goal5325_xhd_public_web_supplement_artifact_sweep_test
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
A broader public web sweep did not find X-HD exact input datasets on author
pages, NSF PAR, ResearchGate, Zenodo/Figshare/OSF-style searches, or BraTS
mirrors. One ACM supplementary zip is visible but inaccessible from this
environment and must be inspected before declaring publication-adjacent
artifacts exhausted.
```

Forbidden:

```text
claiming the ACM supplement contains datasets without inspection;
claiming the ACM supplement contains no useful artifacts without inspection;
claiming all public publication-adjacent artifacts are exhausted while the ACM
zip remains unresolved;
claiming public BraTS mirrors provide X-HD converted point sets or conversion
provenance;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5325 did not use POD.

POD is not expected until concrete input/provenance artifacts appear and need
author `hd_exec` or RTDL verification.
