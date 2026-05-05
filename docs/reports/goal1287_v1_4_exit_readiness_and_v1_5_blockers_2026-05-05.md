# Goal1287 v1.4 Exit Readiness and v1.5 Blockers

Date: 2026-05-05

Status: local v1.4 readiness summary. This is not a public release gate. This
is not a pod evidence packet. This is not public RTX wording authorization.

## Decision

v1.4 is locally exit-ready for the compatibility-wrapper metadata layer:

- the accepted v1.3 primitive contract is represented in app output metadata;
- runtime attachment validates the contract before adding it to app payloads;
- a machine-readable inventory records the current v1.4 app/backend surface;
- a CI/operator gate fails on backend-scope drift, frozen-backend promotion,
  Jaccard diagnostic promotion, or accidental public wording authorization.

This does not mean v1.5 is ready. v1.5 requires native implementation movement
from app-specific wrappers toward generic traversal-plus-reduction primitives.

## Stable v1.4 Surface

Active v1.4 app rows:

| App row | Current v1.4 primitive contract | Active backends | Status |
|---|---|---|---|
| `graph_analytics.visibility_edges` | `ANY_HIT` plus `COUNT_HITS` / `REDUCE_INT(COUNT)` metadata | Embree, OptiX | compatibility wrapper metadata stable |
| `database_analytics.sales_risk` | `COUNT_HITS`, `REDUCE_INT(COUNT)`, `REDUCE_INT(SUM)` metadata | Embree, OptiX | compatibility wrapper metadata stable |
| `polygon_pair_overlap_area_rows` | `ANY_HIT` candidate discovery; `REDUCE_FLOAT(SUM)` deferred | Embree, OptiX | compatibility wrapper metadata stable |
| `polygon_set_jaccard` | `ANY_HIT` candidate discovery; `COLLECT_K_BOUNDED` experimental; score reduction deferred | Embree, OptiX | diagnostic only |

Frozen-before-v2.1 backends:

- Vulkan
- HIPRT
- Apple RT

These backends may keep existing proof surfaces, but they are not active v1.4
engineering targets and must not be promoted by v1.4 or v1.5 work.

## v1.5 Blockers

v1.5 is blocked by these engineering items:

- Generic native primitive ABI: native Embree and OptiX code still needs an
  app-name-free entry surface for `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_INT(COUNT|SUM)`, and `REDUCE_FLOAT(MIN|MAX|SUM)`.
- Reduction implementation: `COUNT_HITS` is closest to stable; integer and
  float reductions still need same-contract result schemas and tolerance rules.
- Same-contract backend parity: Embree remains the CPU RT baseline/fallback and
  OptiX is the NVIDIA RT target, but parity must be tested through the generic
  primitive path, not only app-specific wrappers.
- Fresh NVIDIA performance evidence: next pod work must measure active rows
  through the accepted contract boundaries and preserve environment diversity
  probes.
- Jaccard promotion remains blocked: current status is
  `optix_still_slower_with_reason`; it must stay diagnostic until a bounded
  collection/scoring path has correctness and performance evidence.
- Public wording remains blocked: public RTX wording needs exact-subpath wording
  and 3-AI consensus. Current v1.4 artifacts are internal engineering evidence.

## Next Pod Evidence Packet

Do not start a pod only for this report. When a pod is available, the next
NVIDIA evidence packet should collect:

- environment probe: OS, CUDA, OptiX headers, compiler, GPU, driver, Embree
  version, git commit;
- graph visibility prepared repeats using the existing
  `--visibility-query-repeats` diagnostic;
- DB sales-risk compact-summary warm-query timings with materialization-free
  confirmation;
- polygon-pair candidate discovery plus exact-continuation phase timings;
- Jaccard chunked diagnostic timings, positive-pair parity, and explicit
  explanation if OptiX remains slower than Embree;
- copied artifacts plus an intake report before any performance conclusion is
  accepted.

## Exit Criteria Toward v1.5

v1.4 can be treated as locally complete when:

- Goal1286 inventory gate remains valid;
- the v1.4 regression set passes;
- no frozen backend is promoted before v2.1;
- the next work item starts generic Embree/OptiX primitive implementation
  rather than adding more app-specific metadata.

v1.5 can start when the first generic primitive implementation slice is scoped.
The recommended first slice is `ANY_HIT` plus `COUNT_HITS` for graph
visibility, because it has the narrowest accepted contract and the best prior
OptiX evidence that query traversal itself is fast while scene setup dominates.

## Verification

Focused readiness guard:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test
```

Result: 5 tests passed.

Broader v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test \
  tests.goal1286_v1_4_contract_inventory_gate_test \
  tests.goal1285_v1_4_contract_inventory_export_test \
  tests.goal1284_v1_4_primitive_contract_inventory_test \
  tests.goal1283_v1_4_runtime_contract_validation_test \
  tests.goal1282_v1_4_primitive_contract_schema_test \
  tests.goal1281_v1_4_wrapper_consolidation_status_test \
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

Result: 100 tests passed.
