# Goal1280 v1.4 Polygon Jaccard Diagnostic Contract Metadata

Date: 2026-05-05

Status: local v1.4 diagnostic metadata checkpoint. This intentionally does not
promote Jaccard public wording.

## Change

`polygon_set_jaccard` now attaches a `primitive_contract` payload that records:

- status: `optix_still_slower_with_reason`;
- candidate discovery: `ANY_HIT` when Embree/OptiX native-assisted mode is used;
- experimental collection primitive: `COLLECT_K_BOUNDED`;
- future score primitive: `REDUCE_FLOAT(SUM)`, deferred until generic
  float-reduction contract work;
- exact score continuation: app-specific native C++;
- public wording allowed: `false`;
- chunk policy required for public evidence: `true`.

The change is metadata only. It preserves existing rows, summaries, phase
counters, and native continuation labels.

## Boundary

Jaccard remains diagnostic in v1.4. Native RT traversal may help candidate
discovery, but the stable v1.5 scalar primitive path is not proven here because
bounded collection, chunk policy, and exact set-area scoring remain outside the
stable primitive surface. Public wording remains blocked while OptiX is slower
than Embree.

## Verification

Focused local verification should include:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal1131_polygon_app_phase_contract_test \
  tests.goal1274_v1_3_primitive_contract_test
```

Result: 24 tests passed.

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

Result: 75 tests passed.
