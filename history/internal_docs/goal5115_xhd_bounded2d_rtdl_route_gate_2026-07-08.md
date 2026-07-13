# Goal5115 - X-HD Bounded2D RTDL Route Gate

Date: 2026-07-08

## Verdict

```text
completed_bounded2d_rtdl_public_column_route_matched_author_json
```

## Objective

Move the X-HD paper app one step beyond an app-owned exact comparator by wiring
a real RTDL route into the bounded same-input gate. The target is intentionally
narrow:

- fixture: `bounded2d` WKT, 10 points vs 9 points;
- route: RTDL public 2D columnar Hausdorff APIs;
- comparator: existing author `hd_exec` JSON from the POD run;
- claim: bounded same-input route agreement only.

This goal does not claim full X-HD paper reproduction, exact paper datasets,
3D RTDL route coverage, RT-core equivalence, or performance.

## Implementation

Added:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
tests/goal5115_xhd_rtdl_route_gate_test.py
Paper-reproduction-apps/x-hd-paper/results/bounded2d_rtdl_route_gate_summary.json
```

The runner reads the same WKT fixtures used by the author gate, converts 2D
points into RTDL `Point` rows, then uses:

```text
point_rows_to_numpy_columns
directed_hausdorff_2d_numpy_columns
```

for both directed passes. It compares the resulting Hausdorff value against:

1. the deterministic exact reference used by the existing author gate; and
2. the existing author JSON artifact
   `bounded2d_author_hd_exec_output_pod.json`.

The 3D bounded fixture is explicitly rejected by this runner because the route
is a public 2D Hausdorff API route. Goal5114 remains valid as author-vs-exact
3D same-input evidence, but Goal5115 does not turn it into a 3D RTDL route.

## Result

Generated artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded2d_rtdl_route_gate_summary.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.rtdl_route_gate.v1
route = rtdl_numpy_columns_2d
point_count_a = 10
point_count_b = 9
author_hd_result = 2.0
rtdl_route.hausdorff = 2.0
exact_reference.hausdorff = 2.0
author_abs_diff = 0.0
tolerance = 1e-6
matched = true
```

The route metadata also records that this path is partner/reference columnar
execution, not an RT-core speedup path:

```text
native_engine_row_contract = not_called_partner_reference_only
rt_core_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
direct_device_handoff_authorized = false
```

## Documentation Updates

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/results/README.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

The manifest status is now:

```text
bounded_same_input_author_json_gates_complete__bounded2d_rtdl_route_matched
```

## Verification

Ran:

```text
py -m unittest tests.goal5115_xhd_rtdl_route_gate_test
```

Result:

```text
Ran 3 tests in 1.046s
OK
```

The test suite checks:

- bounded2d RTDL route matches exact reference and existing author JSON;
- reference-only mode makes no author match claim;
- 3D input is rejected until a public 3D RTDL route exists.

## Claim Boundary

Authorized:

- X-HD paper app can run a bounded 2D WKT fixture through a generic RTDL
  public columnar Hausdorff route.
- That route matches the existing author JSON `HDResult` and exact reference on
  the bounded2d fixture.

Not authorized:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- author performance parity;
- whole-program speedup;
- RT-core X-HD algorithm equivalence;
- 3D RTDL route coverage;
- reclassifying the historical `hausdorff_xhd` benchmark as a paper
  reproduction result.

## Next Step

Goal5116 should decide the next bounded RTDL route target:

1. add an optional POD Numba/CuPy route for bounded2d if the environment is
   stable; or
2. design a public 3D Hausdorff route contract before attempting bounded3d
   RTDL route coverage.

The second option is the more language/system-oriented next step; the first is
only a partner-backend smoke extension.
