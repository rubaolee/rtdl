# Goal 686 App Cleanup Review

**Reviewer:** Claude (claude-sonnet-4-6)
**Date:** 2026-04-21
**Verdict:** ACCEPT

---

## Checklist

| Check | Result |
| --- | --- |
| One primary DB app exists | PASS |
| One primary graph app exists | PASS |
| One primary Apple RT demo exists | PASS |
| Spatial join apps honestly documented | PASS |
| Public commands mechanically covered | PASS |
| No overclaim introduced | PASS |

---

## Primary App Surface

### DB App

`examples/rtdl_database_analytics_app.py` exists and is the declared primary.
It imports and delegates to `rtdl_v0_7_db_app_demo.run_app` and
`rtdl_sales_risk_screening.run_case`, unifying both into one `run_app(backend,
scenario)` call. The `honesty_boundary` field in the returned JSON reads:

> "Unified app over bounded v0.7 DB kernels; not SQL, indexes, joins,
> transactions, query planning, or a DBMS."

The `unifies` field lists both source files explicitly. The catalog correctly
labels `rtdl_database_analytics_app.py` as the "primary DB app entry point"
and the older files as "runnable compatibility examples." No DB capability is
implied beyond `conjunctive_scan`, `grouped_count`, and `grouped_sum`.

The backend alias fix is also clean: `rtdl_v0_7_db_app_demo.py` now accepts
`--backend cpu_python_reference` (the public convention), maps it to
`cpu_reference` internally via `_canonical_backend`, and preserves both
`requested_backend` and `backend` in output JSON so callers can see the
translation. The argparse default was aligned to `cpu_python_reference` as
well. No existing code paths were broken.

### Graph App

`examples/rtdl_graph_analytics_app.py` exists and is the declared primary.
It imports `rtdl_graph_bfs.run_backend` and
`rtdl_graph_triangle_count.run_backend`, running both under a
`run_app(backend, scenario)` interface. The `honesty_boundary` field reads:

> "Unified app over bounded v0.6.1 graph kernels; not a full graph database or
> distributed graph analytics system."

The catalog labels `rtdl_graph_analytics_app.py` as the "primary graph app
entry point" and the primitive files as compatibility examples. The graph
surface is correctly bounded to `bfs` and `triangle_count` — no graph-database
or distributed analytics claim.

### Apple RT Demo

`examples/rtdl_apple_rt_demo_app.py` exists and is the declared primary. It
runs two scenarios — `closest_hit` via `rtdl_apple_rt_closest_hit` and
`visibility_count` inline — both wrapped in try/except blocks that produce
`"apple_rt_available": false` / `"status": "skipped"` output when the Apple RT
library is unavailable. The `honesty_boundary` field reads:

> "Unified Apple RT demo; hardware-backed support depends on macOS Apple Silicon
> and a rebuilt librtdl_apple_rt, and this is not a broad Apple speedup claim."

Hardware-gated sections degrade gracefully with explicit unavailability keys
rather than silent fallback or silent omission. The catalog marks this as the
"primary Apple RT demo entry point" and lists both scenario-specific files as
"scenario-specific" examples.

---

## Spatial Join Documentation

All 8 spatial join apps named in the catalog and Goal686 report exist on disk:

- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`
- `examples/rtdl_facility_knn_assignment.py`
- `examples/rtdl_road_hazard_screening.py`
- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`

The catalog describes the RTDL feature shape for each (radius join, KNN join,
segment/polygon join, polygon/polygon overlap join). The honesty boundary is
present and unambiguous:

- "Spatial-join examples are bounded examples, not a full GIS engine."
- "PostGIS is an external baseline and correctness/performance anchor, not an
  RTDL backend."

`docs/sql/` is correctly described as external comparison scripts, not an RTDL
backend. No GIS completeness, query planning, or index capability is implied.

---

## Catalog Linking

All four required public docs link to `application_catalog.md`:

- `README.md` — confirmed present
- `docs/README.md` — confirmed present
- `docs/release_facing_examples.md` — confirmed via "Application Catalog" link
  in the "Choose By Job" table and in the preamble
- `examples/README.md` — confirmed via "spatial join apps" row pointing to
  catalog apps

`tests/goal686_app_catalog_cleanup_test.py::test_public_docs_link_application_catalog`
mechanically verifies this across all four paths.

---

## Public Command Coverage

`scripts/goal515_public_command_truth_audit.py` includes:

```
"python examples/rtdl_graph_analytics_app.py --backend cpu_python_reference",
"python examples/rtdl_database_analytics_app.py --backend cpu_python_reference",
```

Both new unified DB and graph app entry points are in `GOAL513_COMMANDS`. The
audit reports `valid: true`, `252` commands across `14` public docs after the
additions (up from `250`). The Apple RT demo app (`rtdl_apple_rt_demo_app.py`)
runs without a backend flag, consistent with `GOAL593_COMMANDS` coverage of the
hardware-gated Apple RT surface.

`tests/goal513_public_example_smoke_test.py` includes both new unified apps:

```python
("examples/rtdl_graph_analytics_app.py", "--backend", "cpu_python_reference"),
("examples/rtdl_database_analytics_app.py", "--backend", "cpu_python_reference"),
```

`tests/goal686_app_catalog_cleanup_test.py::test_unified_database_graph_and_apple_apps_emit_json`
runs all three unified apps and asserts `payload["app"]` and the expected
`sections` keys — directly exercising the primary app CLI path for each.

---

## Test Sufficiency

| Test | Coverage | Assessment |
| --- | --- | --- |
| `test_db_app_accepts_public_cpu_python_reference_alias` | Runs `rtdl_v0_7_db_app_demo.py --backend cpu_python_reference`; checks `requested_backend`, `backend`, `results` fields | Directly covers the backend alias fix |
| `test_public_app_catalog_names_spatial_join_apps` | Asserts 10 required strings including all 8 app names, PostGIS boundary, GIS disclaimer | Locks catalog content |
| `test_public_docs_link_application_catalog` | Checks all 4 public docs contain `application_catalog.md` | Mechanically verifies linking |
| `test_spatial_join_app_clis_emit_json` | Runs 4 radius/KNN spatial apps with `--backend cpu_python_reference` | Covers primary spatial join CLI path |
| `test_unified_database_graph_and_apple_apps_emit_json` | Runs all 3 unified primary apps; asserts `app` name and both scenario `sections` keys | Primary coverage for the new unified apps |

The 4 polygon spatial apps (`segment_polygon_hitcount`, `segment_polygon_anyhit_rows`,
`polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) are not run in
goal686's own test, but `goal513_public_example_smoke_test` covers
`rtdl_segment_polygon_hitcount.py` and the others are exercised in the
supporting test runs cited in the Goal686 report. This gap is acceptable
for a catalog/cleanup goal.

`tests/goal512_public_doc_smoke_audit_test.py` was extended to include
`docs/application_catalog.md` in `PUBLIC_DOCS`, closing a gap that would
otherwise let dead links accumulate silently in the new catalog.

---

## Overclaim Check

No unbounded performance claims were introduced:

- DB apps: explicitly "bounded v0.7 DB kernels; not SQL, indexes, joins,
  transactions, query planning, or a DBMS."
- Graph apps: explicitly "bounded v0.6.1 graph kernels; not a full graph
  database or distributed graph analytics system."
- Apple RT demo: hardware-gated sections fail gracefully with explicit
  availability keys; no broad Apple speedup claim.
- Spatial joins: "bounded examples, not a full GIS engine."
- The `10x reduction in workload-writing burden` claim in `README.md` is
  scoped as "an engineering-productivity target, not an unbounded speedup
  claim" — unchanged from before this goal.

No new backend capability, performance number, or system boundary was added
beyond what the Goal686 scope declares.

---

## Summary

Goal686 delivers: a public application catalog with honest spatial join
inventory, three new unified primary apps (DB, graph, Apple RT), a safe backend
flag alias for the v0.7 demo, and tests that mechanically lock the key
invariants. All five review checkpoints pass. No overclaims, no unsafe changes,
no broken code paths found.

**ACCEPT**
