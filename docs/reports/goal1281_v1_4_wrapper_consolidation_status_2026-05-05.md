# Goal1281 v1.4 Wrapper Consolidation Status

Date: 2026-05-05

Status: local v1.4 consolidation checkpoint. This is not a public release gate,
not public RTX wording, and not a v1.5 architecture acceptance packet.

## Summary

The accepted Goal1274 v1.3 target rows now have v1.4 compatibility or
diagnostic metadata coverage:

| App row | v1.4 contract status | Stable/diagnostic primitive mapping | Backend scope | Public wording |
| --- | --- | --- | --- | --- |
| `graph_analytics.visibility_edges` | compatibility wrapper metadata plus prepared OptiX count wrapper routing | `ANY_HIT`, summary `COUNT_HITS` / `REDUCE_INT(COUNT)` | Embree + OptiX active | blocked pending separate exact-sub-path wording review |
| `database_analytics.sales_risk` | compact-summary contract metadata | `COUNT_HITS`, `REDUCE_INT(COUNT)`, `REDUCE_INT(SUM)` | Embree + OptiX active | blocked pending separate exact-sub-path wording review |
| `polygon_pair_overlap_area_rows` | candidate-discovery contract metadata | `ANY_HIT`; future `REDUCE_FLOAT(SUM)` deferred | Embree + OptiX active | blocked pending separate exact-sub-path wording review |
| `polygon_set_jaccard` | diagnostic-only contract metadata | `ANY_HIT` diagnostic, `COLLECT_K_BOUNDED` experimental, future `REDUCE_FLOAT(SUM)` deferred | Embree + OptiX active for diagnostics | blocked; status remains `optix_still_slower_with_reason` |

## What Changed In v1.4 So Far

- Each target app row now exposes `primitive_contract` metadata.
- Embree is consistently labeled `cpu_rt_baseline_and_fallback`.
- OptiX is consistently labeled `nvidia_rt_target`.
- Existing Vulkan/HIPRT/Apple RT proof paths are not expanded and are not
  active v1.4 engineering targets.
- Graph OptiX prepared any-hit count now routes through
  `run_prepared_visibility_anyhit_count(...)`, but behavior and phase names are
  preserved.
- DB sales-risk compact-summary behavior, chunking, and materialization-free
  labels are preserved.
- Polygon-pair preserves the Goal1270 diagnostic split: candidate discovery is
  separated from exact positive-pair area continuation.
- Jaccard remains explicitly non-promoted and public-wording blocked.

## Remaining Before v1.5 Architecture Review

This v1.4 state is useful but not enough for v1.5 acceptance. Remaining work:

- Define a normalized primitive-plan schema shared across graph, DB, and
  polygon helpers instead of parallel ad-hoc dictionaries.
- Add schema validation tests for required fields, status values, backend
  roles, and public-wording gates.
- Decide whether Embree needs a prepared visibility-count wrapper for
  prepared-vs-prepared graph parity.
- Decide whether DB compact-summary should move from app metadata to a reusable
  generic primitive wrapper object.
- Keep Jaccard diagnostic unless a later pod proves a stable same-contract
  OptiX improvement and the exact reason is reviewed.
- Run a pod only after local schema normalization is stable; pod time should
  validate same-contract phase counters, not discover basic schema errors.

## Verification

Combined v1.4 wrapper regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test \
  tests.goal1275_v1_4_first_wrapper_slice_plan_test \
  tests.goal1274_v1_3_primitive_contract_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal1131_polygon_app_phase_contract_test \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal1128_embree_db_compact_summary_contract_test \
  tests.goal1156_db_compact_summary_batch_contract_test \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test
```

Result: 77 tests passed.

## Next Local Step

The next local step should be schema normalization before requesting another pod: one small module that defines required `primitive_contract` fields and validates contract dictionaries for graph, DB, polygon-pair, and Jaccard.
