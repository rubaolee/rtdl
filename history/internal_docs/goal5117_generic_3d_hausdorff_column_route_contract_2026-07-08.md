# Goal5117 - Generic 3D Hausdorff Column Route Contract

Date: 2026-07-08

## Verdict

```text
generic_3d_hausdorff_column_route_contract_ready
```

## Objective

Add a generic RTDL 3D Hausdorff column route so bounded3d X-HD evidence does not
remain only an app-owned exact-comparator result.

## Implementation

Added public RTDL exports:

```text
point_rows_to_numpy_columns_3d
directed_hausdorff_3d_numpy_columns
```

Files changed:

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5117_generic_3d_hausdorff_column_route_test.py
```

The route is NumPy/reference columnar, exact, and generic. It uses the existing
`generic_group_argmin_then_global_argmax_with_witness` reducer contract. It does
not call native RT traversal and makes no performance claim.

## Non-X-HD Genericity Proof

The test `goal5117_generic_3d_hausdorff_column_route_test.py` constructs a
synthetic non-X-HD 3D point set and verifies:

- public API is importable from `rtdsl`;
- 3D columns contain `ids/x/y/z`;
- directed 3D Hausdorff distance is correct;
- witness ids are correct;
- metadata records `not_called_partner_reference_only`;
- speedup flags are false;
- implementation window contains no `xhd`, `x-hd`, `paper`, or `hd_exec`.

## Boundary

Authorized:

- RTDL has a generic public 3D NumPy columnar Hausdorff reference route.

Not authorized:

- RT-core X-HD algorithm equivalence;
- device-resident / zero-copy claim;
- performance claim;
- paper reproduction claim.

## Verification

Ran with Goal5118 tests:

```text
py -m unittest tests.goal5117_generic_3d_hausdorff_column_route_test tests.goal5115_xhd_rtdl_route_gate_test tests.goal5118_xhd_bounded3d_rtdl_route_gate_test
```

Result:

```text
Ran 7 tests
OK
```

## Next

Goal5118 applies this route to the bounded3d X-HD paper-app fixture and compares
it against author JSON and exact reference.
