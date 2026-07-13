# Goal5315 - X-HD WaterBodies/BG Status Docs Update Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5315 updates the public/internal status surfaces after Goals5313-5314 so
the WaterBodies -> BlockGroups line no longer appears as an unresolved
Goal5311/Goal5312 mismatch.

The update keeps the old evidence visible:

```text
Goal5311 n_points_cell=15 author rerun remains config-sensitivity evidence.
Goal5313 n_points_cell=8 author rerun is the paper-log denominator.
Goal5314 is the corrected comparison summary.
```

## Files Updated

```text
Paper-reproduction-apps/x-hd-paper/results/README.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
history/internal_docs/xhd_current_status_after_goal5314_2026-07-09.md
tests/goal5315_xhd_water_bg_status_docs_test.py
```

## Status Now Exposed

The results README now includes:

```text
Full-Public WaterBodies -> BlockGroups Corrected Comparison
```

and records:

```text
Goal5311 default author rerun:
  n_points_cell=15
  HDResult=0.8970130085945129

Goal5313 paper-config author rerun:
  n_points_cell=8
  HDResult=0.8964367508888245

RTDL exact-witness:
  float64=0.8964380566690101
  same witness float32=0.8964367508888245
  abs diff=1.305780185645311e-06
  declared tolerance=2e-6
```

The review register now tracks:

```text
Goal5313: implemented_review_pending
Goal5314: implemented_review_pending
```

The new current-status document states that full X-HD paper reproduction is
still incomplete, while the WaterBodies-BG full-public scalar denominator is no
longer unresolved.

## Validation

Commands:

```text
py -m unittest tests.goal5315_xhd_water_bg_status_docs_test

py -m unittest \
  tests.goal5313_xhd_water_bg_n_points_cell_alignment_test \
  tests.goal5314_xhd_water_bg_corrected_comparison_summary_test \
  tests.goal5315_xhd_water_bg_status_docs_test
```

Results:

```text
Ran 3 tests OK
Ran 9 tests OK
```

## Claim Boundary

Still not claimed:

```text
exact paper WKT files recovered;
Figure 5 fully reproduced;
full X-HD paper reproduction complete;
performance parity;
identical author/RTDL internal numeric precision.
```

## Next Recommended Goal

```text
Goal5316: build a consolidated X-HD Figure-5 / Level-B status matrix.
```

The matrix should separate:

```text
exact paper input availability;
same-source public candidate availability;
author paper-config scalar reproduction;
RTDL scalar / witness reproduction;
performance denominator availability.
```

Goal5316 should not require a POD unless a reviewer requests a rerun.
