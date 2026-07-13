# Goal5118 - X-HD Bounded3D RTDL Route Gate

Date: 2026-07-08

## Verdict

```text
bounded3d_rtdl_route_matched_author_json
```

## Objective

Close the bounded route asymmetry: bounded2d already had a real RTDL route, but
bounded3d only had author-vs-exact evidence. This goal applies the generic 3D
Hausdorff route from Goal5117 to the existing bounded3d fixture.

## Implementation

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
tests/goal5118_xhd_bounded3d_rtdl_route_gate_test.py
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/results/README.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

Generated:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded3d_rtdl_route_gate_summary.json
```

## Result

```text
fixture = bounded3d
n_dims = 3
point_count_a = 9
point_count_b = 8
route = rtdl_numpy_columns_3d
author_hd_result = 2.0
rtdl_route.hausdorff = 2.0
exact_reference.hausdorff = 2.0
author_abs_diff = 0.0
tolerance = 1e-6
matched = true
```

The author `HDResult`, RTDL public 3D column route, and deterministic exact
reference agree on the bounded same-input fixture.

## Boundary

Authorized:

- bounded3d same-input RTDL public 3D column route matched author JSON and exact
  reference.

Not authorized:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- author RT-core algorithm equivalence;
- performance claim.

## Verification

Ran:

```text
py -m unittest tests.goal5117_generic_3d_hausdorff_column_route_test tests.goal5115_xhd_rtdl_route_gate_test tests.goal5118_xhd_bounded3d_rtdl_route_gate_test
```

Result:

```text
Ran 7 tests
OK
```

## Next

Goal5119 audits author phase semantics and the meaning of `HDResult` before any
performance matrix or ratio is allowed.
