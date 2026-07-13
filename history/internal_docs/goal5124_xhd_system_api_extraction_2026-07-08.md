# Goal5124 - X-HD System API Extraction

Date: 2026-07-08

## Verdict

```text
xhd_system_api_extraction_complete
```

## Purpose

Separate what the X-HD paper app owns from what became RTDL system/language
capability.

## App-Owned Pieces

The following remain app-owned and must not be promoted into RTDL core:

- author `hd_exec` checkout/build/run wrapper;
- build compatibility patch for the POD toolchain;
- WKT fixture selection and paper workload policy;
- author JSON parser/comparator;
- X-HD tolerance policy;
- paper-app manifest, README, results inventory;
- performance-regime choice and fair-matrix wording.

These pieces are specific to the X-HD artifact and do not belong in the RTDL
language surface.

## System / Generic Pieces

Existing generic assets reused:

- `point_rows_to_numpy_columns`;
- `directed_hausdorff_2d_numpy_columns`;
- `prepare_generic_fixed_radius_count_threshold_2d`;
- generic partner / NumPy / Numba column continuation patterns.

New generic API added during this line:

```text
point_rows_to_numpy_columns_3d
directed_hausdorff_3d_numpy_columns
```

These live under `rtdsl.partner_continuations` and are exported from
`rtdsl.__init__`. They are app-name-free and operate on generic point columns.

## Non-X-HD Genericity Proof

`tests/goal5117_generic_3d_hausdorff_column_route_test.py` uses a synthetic 3D
point set unrelated to X-HD:

```text
source: 3 generic Point3D rows
target: 3 generic Point3D rows
expected directed distance: 2.0
```

It verifies:

- correct distance and witness ids;
- metadata says no native engine row contract was called;
- no RT-core speedup claim is authorized;
- implementation window contains no `xhd`, `paper`, or `hd_exec` identity.

This is the required proof that the new 3D column route is a system capability,
not a paper-app shortcut.

## Fixed-Radius Decision Route Status

The 2D fixed-radius threshold primitive remains a generic RTDL capability and
can express a Hausdorff decision predicate for fixed radius. However, a complete
author-style X-HD iterative route needs additional generic API work and was not
promoted in this closeout.

## Claim Boundary

Authorized:

- RTDL now has a generic public 3D exact columnar directed Hausdorff reference
  route;
- X-HD paper app uses public 2D and 3D columnar routes on bounded fixtures;
- app-specific author and paper comparator code remains outside RTDL core.

Not authorized:

- X-HD-specific RTDL primitive;
- author X-HD RT-core algorithm reproduction;
- performance parity or speedup;
- exact paper dataset reproduction.
