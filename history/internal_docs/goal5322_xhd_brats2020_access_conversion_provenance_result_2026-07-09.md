# Goal5322 - X-HD BraTS2020 Access / Conversion Provenance

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5322 classifies the remaining BraTS2020 ValidationData family in the X-HD
Figure-5 matrix. The question is:

```text
Can we run or claim a BraTS Figure-5 reproduction now, or is this line still
blocked on data access and NIfTI-to-point conversion provenance?
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5322.brats2020_access_conversion_provenance.v1
```

## Evidence Checked

Project evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5214_exact_dataset_availability_refresh_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
```

External official sources:

```text
https://www.med.upenn.edu/cbica/brats2020/data.html
https://www.med.upenn.edu/cbica/brats2020/registration.html
```

## Author Log Evidence

The author paper-branch logs contain a substantial BraTS workload:

```text
category = BraTS2020_ValidationData
unique pairs = 500
records = 2500
repeat count = 5
GPU = NVIDIA GeForce RTX 3090
point count range = 887,826 .. 1,964,247
```

By section:

```text
auto_tune  = 1000 records / 500 unique pairs
eb_gpu     =  500 records / 500 unique pairs
hybrid_gpu =  500 records / 500 unique pairs
rt_gpu     =  500 records / 500 unique pairs
```

Representative Goal5214 pair:

```text
BraTS20_Validation_001_flair.nii -> BraTS20_Validation_033_flair.nii
HDResult = 26.645824432373047
point counts = 1,589,257 / 1,145,851
author paths root = /local/storage/shared/HDDatasets/BraTS2020_ValidationData/...
exact status = author_log_path_known__input_file_not_available
```

This proves the paper-branch workload exists and that author logs have useful
path/count/value metadata. It does not provide the NIfTI files, hashes, or
converted point-set bytes.

## Official BraTS Access Status

The official BraTS 2020 data page points users to the Registration/Data Request
workflow. The registration page describes a CBICA Image Processing Portal
account, manual account approval, a BraTS'20 Data Request job, and a
Results.zip / REGISTRATION_STATUS download-link workflow.

The official data page also states that BraTS multimodal scans are distributed
as NIfTI files and include T1, post-contrast T1/T1Gd, T2, and T2-FLAIR volumes.
Validation data were released without ground-truth labels for participants.

Implication:

```text
BraTS is not a simple public-file download already present in this workspace.
The next real step is authorized access plus file hashing, not POD execution.
```

## Current Availability

Current availability remains:

```text
local workspace assets = absent
current POD assets = absent
current POD /local/storage/shared/HDDatasets = missing
```

Goal5214 already probed the current POD and found the HDDatasets root missing.
Goal5301 records BraTS local and current POD assets as absent.

## Conversion Provenance Gap

Even after authorized data access, exact X-HD reproduction would still need the
author's conversion boundary:

```text
NIfTI volume -> X-HD point set
```

Still missing:

```text
author NIfTI-to-point conversion rule;
threshold / mask / modality selection rule;
coordinate convention;
precision policy;
hashes for converted point sets;
byte-identical regeneration proof.
```

This is especially important because official BraTS data are MRI volumes, not
X-HD-ready point clouds. Author log path names and point counts are not enough.

## Exit Label

```text
brats2020_exact_provenance_not_found__access_and_conversion_blocked
```

## Interpretation

Current status:

```text
paper_log_paths_known__access_and_conversion_blocked
```

BraTS remains blocked by:

```text
data access;
image-file hashes;
author image-list / order;
NIfTI-to-point conversion provenance;
converted point-set hashes or byte-identical regeneration proof.
```

The blocker is not RTDL route code and not POD availability.

## Recommended Next Actions

1. Obtain authorized BraTS2020 validation data through CBICA IPP / BraTS'20 Data
   Request, if project policy permits.
2. Record downloaded file list and hashes.
3. Search author source/history for the NIfTI-to-point conversion rule.
4. Only after data and conversion exist, reproduce one listed author-log pair as
   a Level-B same-source gate.
5. Only after that, consider a larger BraTS matrix.

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5322_brats2020_access_conversion_provenance.json
py -m unittest tests.goal5322_xhd_brats2020_access_conversion_provenance_test
```

Expected:

```text
tests pass; no POD required
```

## Claim Boundary

Allowed:

```text
BraTS2020 has strong author-log workload evidence, but exact reproduction is
blocked on authorized NIfTI access and author NIfTI-to-point conversion
provenance.
```

Forbidden:

```text
BraTS2020 exact paper input recovery;
BraTS Figure-5 reproduction;
full X-HD paper reproduction;
route or performance work before authorized data and conversion provenance;
using author log paths or point counts as exact input proof;
author-vs-RTDL performance ratio.
```

## POD Use

Goal5322 did not use POD.

POD is not expected until authorized BraTS files and a concrete conversion /
verification route exist.
