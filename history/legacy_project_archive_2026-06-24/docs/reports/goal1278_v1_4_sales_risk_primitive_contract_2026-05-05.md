# Goal1278 v1.4 Sales Risk Primitive Contract Metadata

Date: 2026-05-05

Status: local v1.4 implementation checkpoint. This is not public RTX wording
and does not expand active backend scope beyond Embree plus OptiX.

## Change

`sales_risk_screening` now attaches a `primitive_contract` payload. For
`compact_summary`, the contract records:

- `COUNT_HITS` for the predicate-count path;
- `REDUCE_INT(COUNT)` as the grouped-count lowering;
- `REDUCE_INT(SUM)` as the grouped integer revenue-sum lowering;
- Embree as `cpu_rt_baseline_and_fallback`;
- OptiX as `nvidia_rt_target`;
- Vulkan as `compatibility_or_inactive` for v1.4 even if the existing proof path
  still executes.

The change is metadata only. Existing compact-summary execution, chunking,
native continuation labels, phase counters, and row-materialization avoidance
are preserved.

## Boundary

The contract covers only bounded compact-summary DB traversal over the
application-owned denormalized table. It excludes SQL engines, DBMS behavior,
query planning, joins, transactions, database indexes as a product feature, and
row-materializing output.

## Verification

Focused local verification:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal1128_embree_db_compact_summary_contract_test \
  tests.goal1156_db_compact_summary_batch_contract_test
```

Result: 21 tests passed.

Combined graph+DB focused regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test \
  tests.goal1275_v1_4_first_wrapper_slice_plan_test \
  tests.goal1274_v1_3_primitive_contract_test \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal1128_embree_db_compact_summary_contract_test \
  tests.goal1156_db_compact_summary_batch_contract_test \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test
```

Result: 57 tests passed.
