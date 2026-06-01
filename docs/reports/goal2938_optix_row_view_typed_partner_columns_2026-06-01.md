# Goal2938: Generic OptiX Row View to Typed Partner Columns

Date: 2026-06-01
Status: local focused gate passed; pod RayJoin smoke pending

## Purpose

Goal2938 adds a generic bridge from existing `OptixRowView` outputs into typed
partner-owned columns:

`rt.optix_row_view_to_partner_columns(...)`

This directly targets the remaining Spatial RayJoin row/overlay continuation
gap: the prepared count/parity route is fast, but row-bearing continuations
should not force users through app-shaped Python dictionaries before they can
use a partner library.

## Design

The helper accepts an `OptixRowView` and copies selected numeric fields into
Torch, Triton-carrier Torch, or CuPy columns. It records:

- field names and inferred numeric dtypes;
- row count;
- `host_stage_copy_used: true`;
- `python_dict_row_materialization_used: false`;
- no true-zero-copy, release, public speedup, or whole-app claim.

This is deliberately not the final v3-style device-resident RT hit-stream
handoff. It is a clean v2.5 typed primitive payload bridge: app-specific row
meaning stays outside the engine, while partner continuations can consume
generic field columns.

## Files

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `tests/goal2938_optix_row_view_typed_partner_columns_test.py`

## Boundary

Goal2938 does not authorize v2.5 release, public speedup wording, broad RT-core
wording, whole-app speedup wording, true-zero-copy wording, automatic partner
selection wording, package-install wording, paper-reproduction wording, or
app-specific native engine logic.
