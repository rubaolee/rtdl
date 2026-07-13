# Goal5126 - X-HD Directed Semantics Discriminating Gate Amendment

Date: 2026-07-08

## Verdict

```text
implemented_directed_semantics_discriminating_gate__review_pending
```

## Purpose

Address the external review required amendment for Goals5111-5125:

```text
RA-1 directed semantics lacks discriminating evidence.
```

The previous bounded fixtures had:

```text
directed_a_to_b == symmetric_hausdorff_diagnostic
```

so a mistaken symmetric comparator would still pass. This amendment adds a
fixture where the author directed contract and symmetric max differ.

## New Fixture

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_a.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/directed2d_asymmetric_b.wkt
```

Geometry:

```text
A = {(0,0), (1,0)}
B = {(0.5,0), (10,0)}
```

Exact values:

```text
directed_a_to_b = 0.5
directed_b_to_a = 9.0
symmetric_hausdorff_diagnostic = 9.0
```

Therefore this fixture behaviorally distinguishes the author directed
input1-to-input2 contract from a symmetric Hausdorff max.

## POD Author Evidence

Generated on the active POD using the previously built author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Retained artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_author_gate_summary_pod.json
```

Observed:

```text
author_hd_result = 0.5
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 0.5
exact_reference.directed_b_to_a = 9.0
exact_reference.hausdorff = 9.0
abs_diff = 0.0
matched = true
```

If the gate compared author `HDResult` to the symmetric max, this fixture would
compare:

```text
0.5 vs 9.0
```

and fail.

## RTDL Route Evidence

Retained artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_rtdl_route_gate_summary.json
```

Observed:

```text
route = rtdl_numpy_columns_2d
author_hd_result = 0.5
author_comparison_distance = 0.5
exact_reference.hausdorff = 9.0
rtdl_route.hausdorff = 9.0
author_abs_diff = 0.0
matched = true
```

The route still reports the symmetric diagnostic for transparency, but the
author comparison is against `directed_a_to_b`.

## Tests Added

Updated:

```text
tests/goal5111_xhd_author_json_gate_test.py
tests/goal5115_xhd_rtdl_route_gate_test.py
```

New checks:

- author gate summary must match `directed_a_to_b = 0.5`;
- `directed_b_to_a` and symmetric diagnostic must be `9.0`;
- `directed_a_to_b != symmetric`;
- RTDL route must match author `0.5` while retaining symmetric diagnostic `9.0`.

## Claim Boundary

This amendment proves the directed comparator contract for bounded same-input
fixtures. It does not claim:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- author RT-core algorithm equivalence;
- performance parity or speedup.
