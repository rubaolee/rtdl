# Goal3480 - Claude Review: Overlay Output Complexity and Continuation Contract (Goals 3477–3479)

**Reviewer:** Claude (claude-sonnet-4-6)
**Date:** 2026-06-05
**Verdict:** accept

---

## Scope

This review covers the three-goal chain:

- **Goal3477** — external Shapely/GEOS oracle over RTDL relation rows to characterize exact overlay output complexity
- **Goal3478** — v2.8 benchmark runtime gap map refresh splitting scalar exact-area from streamed full-geometry targets
- **Goal3479** — generic app-agnostic continuation contract with `scalar_exact_area` as P0 and `streamed_overlay_geometry` as P1

Files inspected:

- `scripts/goal3477_shape_pair_exact_overlay_output_complexity_oracle.py`
- `docs/reports/goal3477_shape_pair_exact_overlay_output_complexity_oracle_2026-06-05.md`
- `docs/reports/goal3477_shape_pair_exact_overlay_output_complexity_oracle_pod_2026-06-05.json`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `docs/reports/goal3478_v2_8_runtime_gap_after_overlay_output_complexity_2026-06-05.md`
- `tests/goal3478_v2_8_runtime_gap_after_overlay_output_complexity_test.py`
- `src/rtdsl/v2_8_overlay_area_continuation_contract.py`
- `docs/reports/goal3479_overlay_area_continuation_contract_2026-06-05.md`
- `tests/goal3479_overlay_area_continuation_contract_test.py`

---

## Q1: Does Goal3477 correctly characterize exact overlay output complexity without treating Shapely as an RTDL runtime dependency?

**Finding: Yes.**

Shapely is accessed only through `_import_shapely()` imported from the Goal3474 oracle helper. This lazy import lives entirely inside `run_probe()`, which is a standalone probe script path; nothing in `src/rtdsl/` imports Shapely. The pod JSON artifact explicitly records:

```json
"oracle_dependency_scope": "external_cpu_output_complexity_oracle_not_rtdl_runtime_dependency"
```

The `_geometry_complexity()` function consumes standard Shapely geometry attributes (`.geom_type`, `.exterior.coords`, `.interiors`, `.geoms`, `.coords`) and performs no RTDL runtime calls. The script reuses the Goal3474 `_build_oracle_polygons` / `_claim_boundary` / `_import_shapely` infrastructure, extending it with geometry-type categorization and per-row component/vertex accounting. No new RTDL runtime path is opened.

---

## Q2: Do the artifact values support the stated interpretation?

**Finding: Yes, all reported figures match the pod JSON exactly.**

| Measure | Claimed | Pod JSON |
|---|---:|---:|
| active relation rows | 4,543 | `row_count: 4543` ✓ |
| positive exact-area rows | 1,090 | `positive_area_row_count: 1090` ✓ |
| positive `MultiPolygon` rows | 609 | `positive_geometry_type_counts.MultiPolygon: 609` ✓ |
| positive `GeometryCollection` rows | 48 | `positive_geometry_type_counts.GeometryCollection: 48` ✓ |
| total polygon components | 2,801 | `total_polygon_components: 2801` ✓ |
| total output vertices | 42,314 | `total_output_vertices: 42314` ✓ |
| max components per row | 22 | `max_polygon_components_per_row: 22` ✓ |
| max vertices per row | 586 | `max_output_vertices_per_row: 586` ✓ |

One clarification worth recording: the `max_complexity_samples` array captures the row with maximum *vertex* count (row 184, 11 components, 586 vertices), not the row with maximum *component* count. The 22-component maximum is a separate row not represented in the sample list. This is not an error — both statistics are tracked independently and reported correctly — but it means the sample array cannot stand alone as evidence for the 22-component figure. The top-level `max_polygon_components_per_row: 22` field is the authoritative source for that number.

The zero-area breakdown (3,452 boundary-only touch rows + 1 empty row = 3,453 zero-area rows) is consistent with the Goal3474 total of 3,453 zero-area rows.

---

## Q3: Does Goal3478 honestly update the gap map to split near-term scalar exact area from later streamed full-geometry output?

**Finding: Yes.**

The `spatial_rayjoin` entry in `v2_8_benchmark_runtime_gap.py` has been updated at two levels:

- **`current_best_path`** now reads: *"output-complexity oracle evidence shows the full geometry path would require streamed component/vertex output, while the current benchmark target can stay scalar exact-area first"*
- **`current_bottleneck`** records the specific Goal3477 numbers (609 MultiPolygon, 48 GeometryCollection, 2,801 components, 42,314 vertices, max 22/586) and makes the near-term/later split explicit

`Goal3477` is added to `evidence_refs`. The split is also stated clearly in the Goal3478 report as two named targets with distinct timelines.

Validation: `validate_v2_8_benchmark_runtime_gap_map()` returns `"status": "accept"` when called from the test, and the test asserts both phrases (`"scalar exact-area first"` and `"streamed component/vertex output"`) appear in the updated row. All claim authorization fields remain `False` at both the row level and the structural level enforced by `V28BenchmarkRuntimeGapRow.__post_init__`.

---

## Q4: Does Goal3479 define a generic app-agnostic continuation contract with `scalar_exact_area` as P0 and `streamed_overlay_geometry` as P1?

**Finding: Yes.**

`v2_8_overlay_area_continuation_contract.py` defines `V28OverlayAreaContinuationPlan` with:

- Both targets share the same `input_contract = "shape_pair_relation_flags_with_ordinals_and_geometry_payload"` — a generic relation-payload string with no app or domain name
- P0 `scalar_exact_area`: output contract `"row_aligned_float64_exact_area_plus_status"`, algorithm family `"generic_simple_polygon_scalar_area_continuation"`
- P1 `streamed_overlay_geometry`: output contract `"streamed_component_vertex_columns_plus_owner_rows"`, algorithm family `"generic_simple_polygon_full_geometry_stream_continuation"`
- `__post_init__` enforces that no other target string is accepted and no priority other than P0/P1/P2 is valid
- `validate_v2_8_overlay_area_continuation_plan()` enforces that the ordering is strictly scalar-first, then streamed-geometry, and rejects any plan where the priorities are swapped

No RTDL application names, domain terms, or partner names appear in the target strings, algorithm families, or input/output contract strings. The `select_v2_8_overlay_area_continuation_target()` function accepts generic aliases (`"area"`, `"scalar"`, `"geometry"`, `"full_geometry"`) and rejects anything app-specific with an explicit `ValueError`.

---

## Q5: Are all release, speedup, RT-core, true-zero-copy, paper reproduction, hidden dispatch, hidden partner selection, and full-overlay-completion claims still blocked?

**Finding: Yes, blocked at every layer.**

| Layer | Mechanism |
|---|---|
| Pod JSON artifact | `claim_boundary` object with all seven flags `false` |
| `V28BenchmarkRuntimeGapRow.__post_init__` | Raises `ValueError` if any of six flags is `True` |
| `V28OverlayAreaContinuationPlan.__post_init__` | Raises `ValueError` if any of seven flags is `True` (adds `full_overlay_completion_claim_authorized`) |
| `validate_v2_8_benchmark_runtime_gap_map()` | Checks all flags `False` across all rows; returns `"status": "reject"` with error list if any is set |
| `validate_v2_8_overlay_area_continuation_plan()` | Checks all flags `False` across both plans; rejects if claim boundary text is missing required phrases |
| `V2_8_CLAIM_BOUNDARY` string | Explicitly names: release, public speedup, whole-app speedup, broad RT-core, true-zero-copy, paper reproduction, hidden partner selection, hidden dispatch |
| `V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY` string | Adds: full overlay completion claims, app-specific native-engine behavior |
| Test files | Both test classes assert all flags remain `False` via `assertFalse` subtests |

The `full_overlay_completion_claim_authorized` flag is a new addition in Goal3479 that doesn't appear in the older gap map dataclass. The gap map's `V2_8_CLAIM_BOUNDARY` string does not mention "full overlay completion" by name, but the contract module's boundary does. Both modules together provide complete coverage.

---

## Q6: What should the next implementation risk be before writing a GPU scalar-area kernel?

**Finding: Numerical tolerance combined with make_valid-equivalent topology canonicalization is the primary pre-implementation risk.**

The evidence supports this ordering:

1. **Numerical tolerance (must be defined first).** The P0 acceptance bar reads *"must match Goal3474 total exact area within explicit float64 tolerance."* The word *explicit* means the tolerance must be a concrete named value before the kernel is written, not derived post-hoc. GEOS computes intersections using adaptive exact arithmetic internally; a GPU float64 kernel operating on floating-point coordinates will accumulate rounding error that grows with polygon complexity. Without a tolerance budget, the acceptance bar cannot be evaluated.

2. **Topology repair equivalent (must be scoped before kernel design).** The pod artifact shows 9,923 left-side shapes and 596 right-side shapes required `make_valid` repair — approximately 63% of shapes on both sides. If the GPU path skips an equivalent canonicalization step, the kernel will receive degenerate or self-intersecting input polygons, producing incorrect area values or crashes. The acceptance bar says *"must fail closed on unsupported topology,"* but the scope of "unsupported" must be defined: does the kernel reject self-intersecting input, fix it, or assume the host pre-validates? This policy directly constrains the kernel's input interface.

3. **Scratch-capacity policy (secondary, but must precede kernel layout).** Max 22 polygon components and 586 output vertices in a single row establishes the upper-bound scratch requirement. A scalar area continuation can bound this tightly (the output is one float64 per row), but intermediate clip-list storage during Sutherland-Hodgman or Weiler-Atherton steps requires bounded per-thread scratch. The P0 acceptance bar requires *"fail closed on unsupported topology or scratch-capacity overflow,"* so the overflow policy must be part of the kernel specification.

4. **Algorithm family (addressed by contract, but worth confirming scope).** Goal3467 found 4,375 of 4,543 rows require the general simple-polygon overlay path; Goal3471 covers the 168 both-convex rows. The P0 contract names `"generic_simple_polygon_scalar_area_continuation"` as the algorithm family, which correctly excludes convex-only approaches. The implementation decision is which polygon clipping algorithm to use for nonconvex pairs (e.g., Sutherland-Hodgman with ear-clipping, Greiner-Hormann, or a scan-line approach). This affects both the tolerance story and the scratch-capacity story, so it is downstream of items 1–2 but must be settled before item 3 can be fully specified.

In short: define the float64 tolerance budget and the topology repair scope together, then derive the scratch-capacity policy, then choose the algorithm family implementation. Writing the GPU kernel before any of these three are settled risks building to a target that the acceptance bar cannot confirm.

---

## Artifact Traceability

| Item | Evidence |
|---|---|
| Pod host | `root@69.30.85.203 -p 22057` |
| Commit at pod run | `85ff57ff058e9130c9760d94e69434ee24f5e191` |
| GPU | `NVIDIA RTX A5000, driver 580.126.09` |
| Shapely version | `2.1.2` |
| Oracle time | 0.6811 s (single iteration) |
| Relation build time | 0.3736 s |
| Geometry build time | 6.1018 s |

---

## Summary

Goal3477 provides a well-scoped external oracle that characterizes full overlay output complexity without importing Shapely into the RTDL runtime. All seven numeric claims (1,090 positive rows, 609 MultiPolygon, 48 GeometryCollection, 2,801 components, 42,314 vertices, max 22 components, max 586 vertices) are verified directly against the pod JSON. Goal3478 correctly updates the gap map with the scalar/streamed split and preserves all claim blocks through structural enforcement. Goal3479 defines a clean generic contract with scalar-first P0 ordering, no app-specific names, and enforcement mechanisms that reject any attempt to set claim flags. All claims remain blocked at every layer.

**Verdict: accept**
