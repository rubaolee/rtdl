# Call For Review: Goal5322 X-HD BraTS2020 Access / Conversion Provenance

Please strictly review Goal5322.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
tests/goal5322_xhd_brats2020_access_conversion_provenance_test.py
history/internal_docs/goal5322_xhd_brats2020_access_conversion_provenance_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5214_exact_dataset_availability_refresh_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
```

Official sources checked:

```text
https://www.med.upenn.edu/cbica/brats2020/data.html
https://www.med.upenn.edu/cbica/brats2020/registration.html
```

## Goal5322 Summary

Author logs show:

```text
category = BraTS2020_ValidationData
unique pairs = 500
records = 2500
point count range = 887,826 .. 1,964,247
sections = auto_tune, eb_gpu, hybrid_gpu, rt_gpu
```

Representative author-log pair:

```text
BraTS20_Validation_001_flair.nii -> BraTS20_Validation_033_flair.nii
HDResult = 26.645824432373047
point counts = 1,589,257 / 1,145,851
input paths = /local/storage/shared/HDDatasets/BraTS2020_ValidationData/...
```

But:

```text
local workspace assets = absent
current POD assets = absent
current POD HDDatasets root = missing
official BraTS2020 data access requires CBICA IPP / BraTS'20 Data Request
author NIfTI-to-point conversion provenance = absent
converted point-set hashes = absent
```

Exit label:

```text
brats2020_exact_provenance_not_found__access_and_conversion_blocked
```

## Review Questions

1. Does Goal5322 correctly treat author BraTS logs as workload evidence but not
   exact input provenance?
2. Is the official BraTS access classification correct: access requires
   registration/data request and validation data are NIfTI volumes, not RTDL
   point sets?
3. Does the report correctly identify the missing conversion boundary
   `NIfTI volume -> X-HD point set` as a separate blocker from file access?
4. Is it correct that no POD is needed until authorized data and a concrete
   conversion/verification input exist?
5. Are the claim boundaries complete: no BraTS Figure-5 reproduction, no exact
   dataset claim, no route/performance claim?
6. Are the recommended next actions ordered correctly: access + hashes,
   conversion provenance, then one-pair Level-B gate?
7. Is the exit label acceptable?
8. Should BraTS remain an administrative/provenance blocker rather than an RTDL
   route blocker?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5322_brats_access_conversion_blocked
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5322

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
8. ...
```
