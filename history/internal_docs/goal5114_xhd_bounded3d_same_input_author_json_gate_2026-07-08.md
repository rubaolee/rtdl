# Goal5114 - X-HD Bounded3D Same-Input Author JSON Gate

Date: 2026-07-08

## Status

```text
completed_bounded3d_same_input_author_json_gate_matched__author_build_patch
```

Goal5114 extends the X-HD bounded same-input line from 2D WKT fixtures to a
small 3D WKT fixture while retaining exact-reference tractability.

## Fixture

Inputs:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_a.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_b.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_expected.json
```

Fixture shape:

- A is the unit-cube vertices plus an outlier at `(3, 1, 1)`.
- B is the unit-cube vertices with one `0.1` perturbation.
- The A outlier contributes the Hausdorff maximum.

Expected exact reference:

```text
point_count_a = 9
point_count_b = 8
directed_a_to_b = 2.0
directed_b_to_a = 0.1
hausdorff       = 2.0
tolerance       = 1e-6
```

## POD Execution

This reuses the Goal5112 author binary route:

```text
Author+BuildPatch
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Runner command:

```text
python3 run_xhd_author_json_gate.py
  --input1 bounded3d_a.wkt
  --input2 bounded3d_b.wkt
  --n-dims 3
  --author-bin hd_exec
  --author-json xhd_author_bounded3d_optix77.json
  --summary xhd_bounded3d_gate_summary_optix77.json
  --variant rt
  --execution gpu
  --tolerance 1e-6
```

## Result

Primary summary:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_gate_summary_pod.json
```

Author raw JSON:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_hd_exec_output_pod.json
```

Observed:

```text
author_run.returncode = 0
n_dims = 3
author_hd_result = 2.0
rtdl_reference.hausdorff = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

Author stderr includes:

```text
Points A: 9 Points B: 8
Avg Running Time 4.235 ms
HausdorffDistance: distance is 2
```

The timing field is retained as metadata only. It is not a performance claim.

## Verification

Tests:

```text
py -m unittest tests.goal5110_xhd_paper_app_scaffold_test tests.goal5111_xhd_author_json_gate_test tests.goal5113_xhd_bounded2d_author_gate_test tests.goal5114_xhd_bounded3d_author_gate_test
```

Expected:

```text
12 tests OK
```

The Goal5114 test verifies:

- the local exact reference for bounded3d;
- the POD author summary, when present;
- `n_dims == 3`;
- `author_run.returncode == 0`;
- `matched == true`;
- no paper/performance claim flags.

## What This Proves

- The X-HD `Author+BuildPatch` route executes and matches on a bounded 3D WKT
  same-input fixture.
- The app-owned exact Hausdorff comparator handles 3D POINT WKT inputs.
- The bounded line now covers tiny 2D, larger 2D, and small 3D fixtures.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not prove author performance parity or RTDL speedup.
- It does not prove raw unpatched author source execution on this POD.
- It does not prove that existing RTDL Hausdorff benchmark assets reproduce
  paper figures.

## Recommended Next Goal

Start connecting existing RTDL Hausdorff/X-HD-style assets into this paper app
under the same author-comparator discipline. The first integration should
produce an RTDL-side `HDResult` for one bounded WKT fixture and compare it to
the already collected author JSON, without making paper or performance claims.
