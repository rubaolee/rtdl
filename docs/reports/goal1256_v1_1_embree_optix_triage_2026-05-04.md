# Goal1256 v1.1 Embree/OptiX Triage

Date: 2026-05-04

Status: internal v1.1 execution triage.

## Scope

This report starts v1.1 from clean `main` after v1.0 and the Goal1255
three-AI roadmap consensus. It does not change public wording, release claims,
or backend scope.

Active v1.1 engineering scope:

- Embree remains the same-contract CPU RT baseline and fallback.
- OptiX/NVIDIA RTX performance is the top priority.
- Vulkan, HIPRT, and Apple RT receive no new implementation work before v2.1.
- Existing Vulkan/HIPRT/Apple proof surfaces remain documented and tested where
  already present.

## Source Inputs

- `docs/reports/goal1255_three_ai_v1_1_to_v1_5_roadmap_consensus_2026-05-04.md`
- `docs/v1_0_app_acceleration_inventory.md`
- `docs/v1_0_rtx_app_status.md`
- `docs/performance_model.md`
- live matrix APIs:
  - `rtdsl.rtx_public_wording_matrix()`
  - `rtdsl.optix_app_benchmark_readiness_matrix()`
  - `rtdsl.rt_core_app_maturity_matrix()`
  - `rtdsl.app_engine_support_matrix()`

## v1.1 Outcome Taxonomy

Every v1.1 app investigation should end in one of these buckets:

- `optix_improved`: same-contract OptiX evidence improves enough to justify a
  later public wording review packet.
- `optix_still_slower_with_reason`: OptiX remains slower than Embree, but the
  bottleneck is identified and documented.
- `baseline_contract_incomplete`: same-contract Embree/OptiX timing or parity
  evidence is incomplete, so no performance conclusion is allowed.
- `not_worth_v1_2`: the row is valid but not a strong v1.2 performance target
  compared with other blocked rows.

## Target App Triage

| App | Current public wording state | Current evidence boundary | v1.1 task | Exit condition |
| --- | --- | --- | --- | --- |
| `graph_analytics` | `public_wording_blocked` | Valid same-contract evidence exists, but OptiX measured `2.000505 s` versus Embree `1.000280 s`; raw Embree-over-OptiX ratio is `0.50x`. | Profile the bounded `visibility_edges` path and separate OptiX launch/setup, traversal, compatibility fallback, Python orchestration, BFS/frontier, and triangle-set work. | `optix_improved` or `optix_still_slower_with_reason`; no positive public RTX wording unless later reviewed evidence beats the same-contract Embree baseline. |
| `polygon_pair_overlap_area_rows` | `public_wording_blocked` | Valid same-contract evidence exists, but OptiX measured `3.452362 s` versus Embree `2.896597 s`; raw Embree-over-OptiX ratio is `0.84x`. | Profile native-assisted LSI/PIP candidate discovery separately from exact polygon-area continuation and row/output work. | `optix_improved` or `optix_still_slower_with_reason`; claim boundary remains candidate discovery only. |
| `database_analytics` | `public_wording_not_reviewed` | Prepared DB compact-summary traversal/filter/grouping is RT-core ready, but no public speedup wording is authorized. | Build or refresh same-contract Embree/OptiX compact-summary comparison for the materialization-free DB summary path. | `optix_improved` plus external wording packet if positive, or `baseline_contract_incomplete` if comparison evidence is not strict enough. |
| `polygon_set_jaccard` | `public_wording_not_reviewed` | Native-assisted LSI/PIP candidate discovery is RT-core ready, but no public speedup wording is authorized; exact set-area/Jaccard refinement remains outside the RT-core claim. | Refresh same-contract Embree/OptiX candidate-discovery comparison and root-cause chunk-size diagnostic failures before public review. | `optix_improved`, `optix_still_slower_with_reason`, or `baseline_contract_incomplete`; claim boundary remains candidate discovery only. |

## v1.2 Candidate Queue

The v1.2 performance push should prioritize rows that either block public
wording today or can materially strengthen the NVIDIA RTX story under strict
same-contract boundaries.

1. `graph_analytics`: highest risk because OptiX is currently much slower than
   Embree and the OptiX app support matrix reports a compatibility fallback.
2. `polygon_pair_overlap_area_rows`: close enough to Embree that launch,
   batching, or candidate-discovery isolation may plausibly move the result.
3. `database_analytics`: ready but not public-wording-reviewed; needs clean
   same-contract compact-summary evidence before any public wording.
4. `polygon_set_jaccard`: ready but not public-wording-reviewed; chunk-size
   diagnostic failures must be explained before strong public review.

## Required Profiling Boundaries

Each v1.1/v1.2 timing packet must report:

- command, commit, backend, hardware, and environment;
- CPU/Embree baseline command and OptiX command using the same output contract;
- correctness/parity result and tolerance/schema;
- prepared/setup timing versus repeated-query timing where applicable;
- launch/setup time, native traversal time, native continuation time, and
  Python/output materialization time when available;
- explicit list of excluded phases that remain outside the claim.

## Non-Goals

- No whole-app speedup claims.
- No DBMS, SQL-engine, graph-database, PostGIS, FAISS/HNSW, or full GIS claims.
- No public wording updates without a separate external review packet.
- No v1.5 native-generic refactor before v1.3 contracts are written and
  externally reviewed.
- No new Vulkan, HIPRT, or Apple RT implementation work before v2.1.

## Immediate Next Actions

1. Inspect the graph OptiX compatibility fallback and identify whether a direct
   native path exists or whether the fallback is the expected v1.1 state.
2. Inspect polygon pair/Jaccard candidate-discovery timing instrumentation to
   ensure exact refinement and row work are separated from the RT sub-path.
3. Prepare a pod packet only when local code inspection identifies the exact
   benchmark commands and the expected artifacts.
4. Keep all v1.1 outputs internal until a public wording packet is reviewed by
   at least Codex plus one independent external AI.

## Local Observations Before Pod

Local source-tree checks on this Mac can validate CPU/Embree shape and command
surface, but they cannot produce OptiX timing because `librtdl_optix` is not
available locally.

- `graph_analytics` Embree `visibility_edges` summary runs and reports
  `query_visibility_pair_rows_sec` plus input/postprocess phases. The equivalent
  OptiX command fails locally with `librtdl_optix not found`, so RTX timing is a
  pod-only step.
- `polygon_pair_overlap_area_rows` Embree summary runs and reports separate
  `rt_candidate_discovery_sec` and `native_exact_continuation_sec` phases.
- `polygon_set_jaccard` Embree summary runs and reports separate
  `rt_candidate_discovery_sec`, `native_exact_continuation_sec`, and
  `summary_postprocess_sec` phases.
- `database_analytics` Embree compact-summary profiling reports
  `row_materializing_operation_count = 0`,
  `compact_summary_operation_count = 6`, and
  `phase_clean_candidate_for_rtx_review`. OptiX profiling is skipped locally for
  the same missing-library reason.

Conclusion: continue local code inspection and packet preparation now; start a
pod only when ready to collect same-contract OptiX timings for these four rows.

## First Local Command Packet

These commands are local/source-tree checks. They do not replace RTX pod timing,
but they should be run before spending pod time so the pod packet is narrow.

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py \
  --backend optix --scenario visibility_edges --output-mode summary \
  --copies 1 --require-rt-core
```

Expected local inspection target: confirm `native_continuation_backend` is
`optix_prepared_visibility_anyhit_count` and record the split between
`ray_pack_sec`, `scene_prepare_sec`, `ray_prepare_sec`,
`query_anyhit_count_sec`, and `summary_postprocess_sec`.

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py \
  --backend optix --scenario bfs --output-mode summary \
  --copies 1 --optix-graph-mode native
```

Expected local inspection target: determine whether native graph-ray mode is
usable for diagnostics while remaining outside public RT-core wording.

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py \
  --backend embree --copies 1 --output-mode summary

PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py \
  --backend optix --copies 1 --output-mode summary --require-rt-core
```

Expected local inspection target: compare `rt_candidate_discovery_sec` against
`native_exact_continuation_sec`; only the former is the candidate RT sub-path.

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py \
  --backend embree --copies 1 --output-mode summary

PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py \
  --backend optix --copies 1 --output-mode summary --require-rt-core
```

Expected local inspection target: verify phase separation and candidate counts
before any larger chunk-size diagnostic.

```bash
PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py \
  --backend embree --backend optix --scenario all --copies 1 \
  --iterations 3 --output-mode compact_summary
```

Expected local inspection target: verify that compact-summary runs avoid row
materialization and export phase/counter fields where the backend supports
them.
