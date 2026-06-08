# Goal3857: Claude Review of Goal3856 Triangle-Counting RT-Graph Scale Route

Date: 2026-06-08
Reviewer: Claude (independent, read-only, static/source/artifact review — see Validation note)

## Scope Reviewed

- Commit `1d38d156` ("Goal3856 fix triangle scale route")
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `docs/reports/goal3828_current_benchmark_scale_profile_registry_2026-06-07.md`
- `docs/reports/goal3856_triangle_counting_rt_graph_scale_route_2026-06-08.md`
- `docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/` (`summary.json` and the `.stdout.json` artifact)
- `tests/goal3856_triangle_counting_rt_graph_scale_route_test.py`

## Verdict: **accept**

## Findings by Question

### 1. Does `--rt-graph-copies` preserve edge-file behavior while allowing repeated fixture inputs?

Yes. The new `_repeat_fixture_edges` helper (`rtdl_triangle_counting_benchmark_app.py:1624-1634`) only activates for fixture inputs and offsets each copy's vertex ids by `copy_index * vertex_span`, where `vertex_span = max(endpoint) + 1`. For `degree_oriented_two_triangles` (5 edges, vertex span 4), this produces fully disjoint vertex ranges per copy, so no spurious cross-copy triangles or two-hop relations are introduced — the per-copy oracle/ray/primitive counts scale linearly. This is exactly what the unit test `test_rt_graph_fixture_copies_preserve_oracle_count` checks at `copies=3` (oracle 6, weighted count 6, primitive 15, ray 6 — all `5×3`/`2×3` as expected), and the A5000 artifact confirms it at `copies=2048` (`10240 = 5×2048`, `4096 = 2×2048`).

Edge-file behavior is preserved and explicitly guarded in three independent spots:
- `rt_graph_2a1_generic_rt_payload` and `rt_graph_1a2_generic_rt_payload` both raise `ValueError("--rt-graph-copies applies only to fixture inputs")` when `use_cupy_summary` is true and `rt_graph_copies != 1` (lines 726-727, 902-903).
- `_load_rt_graph_edges` independently raises `ValueError("--rt-graph-copies applies only when --edge-file is omitted")` for both `text` and `binary` edge-file formats when `fixture_copies != 1` (lines 1611-1619).

This double guard means any edge-file path — whether or not it goes through the cupy-summary branch — rejects non-`1` copy values, and the default (`rt_graph_copies=1`) is a no-op (`_repeat_fixture_edges` returns `edges` unchanged when `copies == 1`), so existing edge-file callers and the default fixture path are unaffected.

### 2. Does the scale-profile row now use `rt_graph_2a1_generic_rt` instead of the old `mode=run` fallback?

Yes. `src/rtdsl/current_benchmark_scale_profiles.py:339-365` now builds the `triangle_counting` row as:

```
--mode rt_graph_2a1_generic_rt --backend optix --fixture degree_oriented_two_triangles
--rt-graph-copies 2048 --detail summary --repeat 3 --warmup 1
```

replacing the old `--mode run --backend optix --output-mode summary --optix-graph-mode native --copies 2048` row. The `row_id` was renamed to `triangle_counting_optix_rt_graph_2a1_scale_default_2048`, `purpose` was updated, and `evidence_refs` now includes `"Goal3856"` alongside the prior `"Goal3827"`. `--optix-graph-mode` and `--output-mode` no longer appear, matching `test_scale_registry_uses_rt_graph_prepared_summary_route`'s `assertNotIn("--optix-graph-mode", command)` / `assertNotIn("host_indexed", command)`. The Goal3828 registry doc table and its supersession note (lines 58, 97-101) were updated consistently with the same row id and rationale.

### 3. Is the A5000 artifact internally consistent?

Yes, every cited number checks out against `summary.json` and the `.stdout.json` payload:

| Claim | Artifact value | Verified |
| --- | --- | --- |
| oracle count `4096` | `oracle_triangle_count: 4096` | ✓ |
| RTDL weighted count `4096` | `generic_rt_weighted_triangle_count: 4096`, `generic_rt_summary.weighted_hit_sum: 4096` | ✓ |
| `triangle_count_matches_oracle` | `true` | ✓ |
| primitive/ray counts `10240/4096` | `primitive_count: 10240`, `ray_count: 4096` | ✓ |
| hot query median ≈ `0.214 ms` | `timing_ms.query_median_ms: 0.21430663764476776` | ✓ |
| no row materialization | `generic_rt_summary.rows_materialized: false`, `hit_rows.materialized: false` | ✓ |
| zero claim-flag violations | `summary.json rows[0].semantic_stdout_check.claim_flag_violations: []` | ✓ |
| route / native symbol | `mode: rt_graph_2a1_generic_rt`, `rt_core_path: generic_prepared_triangle_scene_3d_any_hit_weighted_sum`, `v2_4_prepared_session.native_symbols: ["rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum"]` | ✓ |
| fixture copies | `rt_graph_fixture_copies: 2048`, `input_source.rt_graph_copies: "2048"` | ✓ |
| repeat/warmup honored | `timing_ms.query_repeat: 3`, `timing_ms.query_warmup: 1` | ✓ |
| `all_pass`, `status: pass`, `stderr_bytes: 0` | all present and matching in `summary.json` | ✓ |

The arithmetic is also internally coherent: `5 edges × 2048 copies = 10240` directed edges/primitives, `2 triangles × 2048 = 4096` oracle triangles and two-hop rays, and the disjoint-copy construction (vertex span 4, no overlap) means the per-copy counts scale exactly linearly with no cross-copy contamination — consistent with `rt_graph_contract.duplicate_two_hop_relation_count: 4096` and `removed_*` fields all `0`.

### 4. Does the report avoid overclaiming?

Yes. The report explicitly frames the change as "a route correction, not a public same-contract speedup claim" (line 85), names the prior fallback path and its measurement (`host_indexed_fallback`, `query_raw_view_sec` near `0.896843 s`) as a "useful... bottleneck diagnosis" but "not the approved RT-Graph 2A1 benchmark contract" (lines 86-88), and closes the Interpretation section with an explicit non-authorization list: "this goal does not authorize release, broad RT-core speedup, paper-reproduction, true-zero-copy, or whole-app speedup claims" (lines 96-98). It also correctly attributes the dominant process-elapsed cost to startup/imports/contract-construction/scene-prep rather than to the hot query (lines 95-96), and the cited `0.896843` figure for the old fallback matches Goal3855's report (`docs/reports/goal3855_current_scale_after_numba_hot_accounting_2026-06-08.md:67`).

### 5. Required-before-next-step fixes?

None found. Specifically:
- The registry row, its `purpose`, `row_id`, and `evidence_refs` are mutually consistent and match the A5000 artifact's `row_id`.
- The Goal3828 registry doc's table entry and supersession paragraph correctly reference the new row id and Goal3856.
- I grepped the repo for the retired row id `triangle_counting_optix_scale_default_native_2048` and `host_indexed_fallback`; the only "live" references are historical/point-in-time artifacts (other goals' dated reports/snapshots, e.g. Goal3844/Goal3850/Goal3855 A5000 dirs), which correctly remain as frozen evidence of past runs and should not be rewritten.
- The new test file's four assertions (route shape, registry command shape, A5000 artifact contents, report wording) all line up with what is actually present in the artifacts and source as enumerated above.

## Validation

The harness blocked execution of the requested unittest commands (`PYTHONPATH=src;. py -3 -m unittest tests.goal3856_triangle_counting_rt_graph_scale_route_test tests.goal3828_current_benchmark_scale_profile_registry_test`) — both direct invocation and environment-variable-setting forms returned "command requires approval" / "modifies environment variables" without a path to approval. This review is therefore grounded entirely in static source review (the `1d38d156` diff), direct artifact inspection (`summary.json`, the `.stdout.json` payload, the fixture definitions in `rt_graph_contract.py`), and cross-checking the test assertions against those same artifacts — all of which were independently re-derived and matched, as tabulated above.

## Summary

The `--rt-graph-copies` knob is correctly scoped to fixture inputs, guarded redundantly against edge-file misuse, and produces disjoint per-copy graphs that scale oracle/primitive/ray counts linearly and verifiably. The scale-profile registry row now points at the intended `rt_graph_2a1_generic_rt` prepared generic route (replacing the stale `mode=run --optix-graph-mode native` host-indexed fallback), and every number in the A5000 evidence packet — oracle/weighted counts, primitive/ray counts, hot-query median, no-materialization, and zero claim-flag violations — checks out against the raw artifacts. The report is appropriately scoped as a route correction with an explicit non-authorization boundary, and accurately cites the prior fallback's measurement for context. No required-before-next-step fixes identified.
