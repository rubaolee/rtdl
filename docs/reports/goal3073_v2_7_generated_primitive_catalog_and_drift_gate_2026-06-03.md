# Goal3073: v2.7 Generated Primitive Catalog And Drift Gate

Date: 2026-06-03

Status: implemented locally, pending external review.

## Purpose

Goal3070 added primitive discovery metadata and a duplicate gate. The next
v2.7 risk was documentation drift: `docs/rtdl_primitive_catalog.md` could still
be hand-edited away from `src/rtdsl/primitive_hierarchy.py`.

Goal3073 makes the catalog generated from the Python hierarchy source of truth
and adds a test that fails if the checked-in Markdown drifts.

## What Changed

Added:

- `src/rtdsl/primitive_catalog.py`
- `scripts/generate_rtdl_primitive_catalog.py`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`

Regenerated:

- `docs/rtdl_primitive_catalog.md`

The generated catalog includes:

- source-of-truth warning and generator path;
- primitive definition and app-boundary examples;
- approved layer order;
- validation snapshot;
- generated hierarchy tree;
- generated per-layer node tables;
- generated discovery metadata tables;
- controlled discovery facets;
- app-owned boundary exclusions;
- promotion guardrails;
- claim boundary.

## Drift Gate

The test compares `docs/rtdl_primitive_catalog.md` byte-for-byte against
`render_primitive_catalog_markdown()`. It also checks that every hierarchy node
id appears in the catalog and that the generator script's `--check` mode reports
no drift.

## Stale Wording Fixed

Generating the catalog surfaced a stale current-source phrase:

- old: `Triton-first Partner Continuation`
- new: `Explicit Partner Continuation`

The node id remains `continuation.partner_resident`. The new wording reflects
the v2.6/v2.7 boundary: partner choice is explicit user/runtime metadata, not
hidden routing or native-engine policy. The older v2.5 pivot test was updated
to check the current wording while preserving its historical v2.5 plan checks.

## Boundary

This goal does not:

- add orchestration recipes;
- auto-select partners;
- change native engine ABI;
- add app-shaped primitives;
- authorize release readiness;
- authorize speedup, zero-copy, broad RT-core, or paper-reproduction claims.

The generated catalog is an internal architecture catalog and discovery aid.

## Verification

Ran on Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test tests.goal2676_v2_5_triton_partner_pivot_test
```

Result:

```text
Ran 27 tests in 0.029s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

Also ran:

```powershell
py -3 -m py_compile src/rtdsl/primitive_catalog.py scripts/generate_rtdl_primitive_catalog.py src/rtdsl/primitive_hierarchy.py tests/goal3073_v2_7_generated_primitive_catalog_test.py tests/goal2676_v2_5_triton_partner_pivot_test.py
```

Result: clean.
