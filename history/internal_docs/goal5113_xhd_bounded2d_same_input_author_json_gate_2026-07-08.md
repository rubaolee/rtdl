# Goal5113 - X-HD Bounded2D Same-Input Author JSON Gate

Date: 2026-07-08

## Status

```text
completed_bounded2d_same_input_author_json_gate_matched__author_build_patch
```

Goal5113 extends Goal5112 from the 3x3 tiny WKT fixture to a larger bounded
2D same-input fixture:

```text
point_count_a = 10
point_count_b = 9
```

The author `hd_exec` route is still the documented `Author+BuildPatch` route
from Goal5112. No additional author source changes were made.

## Fixture

Inputs:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded2d_a.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded2d_b.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded2d_expected.json
```

Fixture shape:

- A is a 3x3 grid plus one outlier at `(4, 1)`.
- B is a slightly perturbed grid containing `(2, 1)`.
- The A outlier contributes the maximum nearest-neighbor distance.

Expected exact reference:

```text
directed_a_to_b = 2.0
directed_b_to_a = 0.10000000000000009
hausdorff       = 2.0
tolerance       = 1e-6
```

## POD Execution

POD author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Runner command:

```text
python3 run_xhd_author_json_gate.py
  --input1 bounded2d_a.wkt
  --input2 bounded2d_b.wkt
  --author-bin hd_exec
  --author-json xhd_author_bounded2d_optix77.json
  --summary xhd_bounded2d_gate_summary_optix77.json
  --variant rt
  --execution gpu
  --tolerance 1e-6
```

## Result

Primary summary:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded2d_author_gate_summary_pod.json
```

Author raw JSON:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded2d_author_hd_exec_output_pod.json
```

Observed:

```text
author_run.returncode = 0
author_hd_result = 2.0
rtdl_reference.hausdorff = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Author stderr includes:

```text
Points A: 10 Points B: 9
Avg Running Time 3.873 ms
HausdorffDistance: distance is 2
```

The author timing is recorded as metadata only. It is not a performance claim.

## Verification

Tests:

```text
py -m unittest tests.goal5110_xhd_paper_app_scaffold_test tests.goal5111_xhd_author_json_gate_test tests.goal5113_xhd_bounded2d_author_gate_test
```

Expected:

```text
10 tests OK
```

The Goal5113 test verifies:

- the local exact reference for bounded2d;
- the POD author summary, when present;
- `author_run.returncode == 0`;
- `matched == true`;
- no paper/performance claim flags.

## What This Proves

- The `Author+BuildPatch` `hd_exec` route is not limited to the 3x3 tiny
  fixture.
- A larger bounded 2D WKT same-input fixture also matches the deterministic
  RTDL exact Hausdorff reference.
- The app-owned comparator path remains fail-closed and explicitly bounded.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not prove author performance parity or RTDL speedup.
- It does not prove raw unpatched author source execution on this POD.
- It does not prove that existing RTDL Hausdorff benchmark assets reproduce
  paper figures.

## Recommended Next Goal

Choose one:

1. Add a bounded 3D WKT same-input gate, still small enough for exact reference.
2. Start mapping the existing RTDL Hausdorff/X-HD-style assets into this paper
   app with the same author-comparator discipline.

Do not move to paper figures or performance until exact paper inputs and fair
regimes are pinned.
