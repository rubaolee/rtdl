# Goal3105: v2.7 Internal Closeout And v2.8 Runtime Gap Kickoff

Date: 2026-06-03

Status: v2.7 closed as an internal version; v2.8 started as a benchmark-runtime lane.

## Decision

v2.7 is now closed as an internal version. It is not a release tag and does not
authorize public claims. Its value is the primitive discovery/orchestration
layer:

- source-of-truth primitive hierarchy;
- controlled discovery metadata;
- generated primitive catalog;
- duplicate-gated primitive promotion;
- composition recipes;
- explain-only advisory planner;
- optional deterministic semantic search preview.

The current v2.7 closeout is:

- `docs/reports/goal3102_v2_7_post_semantic_search_current_closeout_2026-06-03.md`
- `docs/reports/goal3104_v2_7_post_d8_closeout_2ai_consensus_2026-06-03.md`

## v2.8 Purpose

v2.8 moves back from metadata ergonomics to benchmark-runtime engineering. The
goal is to improve how the generic RTDL runtime carries RT hit/result streams
into grouped continuations, partner continuations, and bounded witness pages
without adding app-specific native engine logic.

The v2.8 kickoff adds a machine-readable gap map in:

- `src/rtdsl/v2_8_benchmark_runtime_gap.py`

## Ten Benchmark Apps

The v2.8 gap map covers the promoted benchmark set:

| Benchmark app | Current bottleneck | First generic runtime target |
| --- | --- | --- |
| Hausdorff / X-HD style | witness/frontier continuation is still harness-shaped | typed nearest-witness streams plus grouped max-distance continuation |
| Spatial RayJoin | row streams, parity/count grouping, and boundary witnesses need reusable continuation | typed hit streams with grouped parity/count and compact-mask continuation |
| RT-DBSCAN | dense adjacency streams and component expansion need device-resident grouped continuation | typed adjacency streams plus grouped component-continuation handoff |
| Robot collision | flag compaction and optional witness rows need shared bounded-output contract | bounded flag/witness result pages with prepared-scene residency metadata |
| Contact manifold | contact witnesses need typed pages and stable overflow semantics | typed bounded witness pages with fail-closed completion metadata |
| RayDB-style grouped aggregates | unfused grouped min/max/stats/witness handoff must not slow fused primitive rows | typed grouped-reduction streams with explicit fused-vs-continuation selection |
| Barnes-Hut / RT-BarnesHut style | frontier rows and force-vector continuation need reusable grouped vector contract | typed aggregate-frontier streams plus grouped vector continuation |
| LibRTS-style spatial index | mutable index/update policy remains app-owned | prepared spatial-index residency and no-regression query harness |
| RTNN neighbor search | packed/prepared column input, replay/chunking, and top-k handoff need first-class support | typed ranked-summary streams with prepared packed-column residency |
| Triangle counting | segmented/streamed graph lowering and candidate-row continuation remain scale limiters | typed graph candidate streams with segmented compact-mask continuation |

## First v2.8 Runtime Target

The first engineering target is:

```text
typed_device_resident_result_streams_and_grouped_continuation
```

This target is deliberately generic. It is not a RayJoin primitive, DBSCAN
primitive, RayDB primitive, Hausdorff primitive, or graph primitive. It is a
shared runtime capability for typed output columns, grouped continuation, and
bounded stream/page metadata that multiple benchmark apps can use.

It is the right first target because it covers the shared bottleneck behind at
least these rows:

- `hausdorff_xhd`
- `spatial_rayjoin`
- `rt_dbscan`
- `robot_collision`
- `contact_manifold`
- `raydb_style`
- `barnes_hut`
- `rtnn`
- `triangle_counting`

`librts_spatial_index` stays lower priority because its next problem is more
about prepared residency and mutable-index policy than the first row-stream
extension.

## What v2.8 Is Not

Goal3105 does not authorize:

- a v2.8 release;
- public speedup wording;
- whole-app speedup wording;
- broad RT-core wording;
- true-zero-copy wording;
- paper reproduction claims;
- hidden partner selection;
- hidden dispatch;
- app-specific native engine behavior.

User-defined shader injection remains a later v3.0 lane, not the first v2.8
target.

## Validation

Machine-readable validation:

```text
validate_v2_8_benchmark_runtime_gap_map()
```

Expected status: `accept`.

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3105_v2_8_benchmark_runtime_gap_map_test tests.goal3102_v2_7_post_semantic_search_current_closeout_test tests.goal3099_v2_7_semantic_search_preview_test
```

Result:

```text
Ran 14 tests in 0.052s

OK
```

Syntax validation:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_benchmark_runtime_gap.py src\rtdsl\__init__.py tests\goal3105_v2_8_benchmark_runtime_gap_map_test.py
```

Result: pass.
