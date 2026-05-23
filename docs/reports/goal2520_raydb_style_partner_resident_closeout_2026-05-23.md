# Goal2520 RayDB-Style Partner-Resident Closeout

Date: 2026-05-23

## Verdict

The RayDB-style benchmark app is complete as an RTDL language/runtime
reconstruction harness through Goal2519.

It is not a RayDB reproduction. It is not a SQL engine, DBMS path, authors-code
comparison, public speedup claim, true zero-copy claim, or whole-app
acceleration claim. Native RTDL is not a RayDB-specific engine.

The app has served its intended purpose: it forced RTDL to separate
database-shaped Python semantics from app-neutral native grouped-reduction
primitives and to expose a clearer Python+partner+RTDL boundary.

## Completed Scope

The final app covers these same-contract result modes:

- `count`
- `sum`
- `min`
- `max`
- `avg_as_sum_count`

Completed implementation/evidence:

- CPU oracle for grouped `count`, `sum`, `min`, `max`, and
  `avg_as_sum_count`.
- Embree count/sum parity through generic columnar payload support.
- OptiX count/sum parity through generic columnar payload support.
- Direct columnar record-set preparation and typed host-buffer handoff work.
- Experimental OptiX partner-resident CUDA tensor descriptor path.
- Native partner-resident grouped i64 `count`, `sum`, `min`, and `max`.
- Explicit dense non-negative `group_capacity` contract.
- Compact grouped output materialization instead of capacity-sized Python
  output materialization.
- Composite `avg_as_sum_count` lowering.
- Generic fused native `sum_count` grouped reduction, with no native average
  ABI.
- One Python runtime dispatcher for partner-resident grouped i64 reductions:
  `run_optix_partner_resident_columnar_grouped_i64_reduction(...)`.
- RayDB-style app dispatches by generic reduction names and no longer selects
  low-level native symbols directly.

## Backend Status

| Backend | Status | Modes | Boundary |
| --- | --- | --- | --- |
| CPU Python reference | Complete | `count`, `sum`, `min`, `max`, `avg_as_sum_count` | oracle only; no native acceleration claim |
| Embree | Complete for parity slice | `count`, `sum` | generic columnar payload path |
| OptiX compatibility path | Complete for parity slice | `count`, `sum` | generic columnar payload path; requires CUDA runtime |
| OptiX partner-resident experimental | Complete for benchmark slice | `count`, `sum`, `min`, `max`, `avg_as_sum_count` | CUDA tensor descriptors, explicit capacity, compact grouped output, dispatcher boundary |

The partner-resident path is the app's final RTDL design contribution. It
demonstrates Python app semantics plus partner-owned CUDA tensor storage plus
app-neutral RTDL grouped reductions.

## Evidence

Local validation after Goal2519:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2493_raydb_code_intake_test \
  tests.goal2494_raydb_style_contract_design_test \
  tests.goal2495_raydb_style_cpu_reference_fixture_test \
  tests.goal2496_raydb_style_embree_lowering_decision_test \
  tests.goal2497_raydb_style_embree_count_sum_parity_test \
  tests.goal2498_raydb_style_optix_count_sum_parity_test \
  tests.goal2499_raydb_style_lowering_plan_test \
  tests.goal2500_raydb_style_backend_matrix_runner_test \
  tests.goal2501_raydb_style_optix_pod_packet_test \
  tests.goal2501_raydb_style_optix_pod_results_test \
  tests.goal2502_raydb_style_benchmark_slice_closeout_test \
  tests.goal2503_direct_columnar_record_set_preparation_test \
  tests.goal2504_columnar_typed_host_buffer_handoff_test \
  tests.goal2505_partner_resident_columnar_descriptor_contract_test \
  tests.goal2506_optix_partner_resident_native_execution_boundary_test \
  tests.goal2507_optix_device_column_abi_scaffold_test \
  tests.goal2508_optix_partner_resident_python_scaffold_test \
  tests.goal2509_optix_partner_resident_scaffold_pod_probe_packet_test \
  tests.goal2510_optix_device_column_abi_validation_test \
  tests.goal2511_optix_partner_resident_device_grouped_i64_execution_test \
  tests.goal2512_raydb_style_partner_resident_experimental_backend_test \
  tests.goal2513_partner_resident_group_capacity_contract_test \
  tests.goal2514_partner_resident_compact_grouped_output_test \
  tests.goal2515_partner_resident_grouped_min_max_i64_test \
  tests.goal2516_partner_resident_composite_avg_sum_count_test \
  tests.goal2517_partner_resident_fused_sum_count_i64_test \
  tests.goal2518_partner_resident_fused_sum_count_timing_test \
  tests.goal2519_partner_resident_grouped_i64_dispatch_boundary_test
```

Result: 145 tests passed, 4 skipped.

Pod evidence:

- `docs/reports/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod_2026-05-23.json`
- status: `ok`
- CUDA available: `true`
- dispatcher reductions: `["count", "sum", "min", "max", "sum_count"]`
- app uses dispatcher: `true`
- app direct low-level grouped symbols absent: `true`
- direct dispatcher cases match CPU reference: `true`
- app suite matches CPU reference: `true`

Goal2518 internal timing evidence:

- `docs/reports/goal2518_partner_resident_fused_sum_count_timing_pod_2026-05-23.json`
- fused `sum_count` matched the two-launch reference.
- internal synthetic subpath ratio: about `5.018x` versus separate sum/count
  launches.
- This remains internal subpath evidence only. It does not authorize public
  speedup, whole-app speedup, SQL, DBMS, authors-code, or true zero-copy
  wording.

## Main RTDL Design Conclusions

The useful reconstruction from this app is:

```text
Python app semantics
+ normalized columnar aggregate plan
+ partner-resident column descriptors
+ generic grouped i64 reductions
+ explicit dense group capacity
+ compact grouped result materialization
+ standardized fail-closed metadata
```

The native engine should not learn RayDB, SQL, SSB, or DBMS vocabulary. The app
may talk in database-shaped terms; the runtime boundary should talk in generic
operations such as `count`, `sum`, `min`, `max`, and `sum_count`.

Composite aggregates should lower in Python to generic runtime primitives. For
this app, `avg_as_sum_count` remains an app semantic, while the runtime executes
`sum_count`.

The dispatcher boundary from Goal2519 is the right stopping point for this
benchmark slice: the app no longer chooses low-level native symbols, and the
runtime emits uniform metadata for correctness, launch count, fused status,
capacity, zero-copy boundary, and performance-claim boundary.

## Remaining Limitations

These limitations are explicit and acceptable for this app closeout:

- fixture is tiny and synthetic;
- group keys must be dense non-negative i64 values below explicit
  `group_capacity`;
- partner-resident native path currently supports one group key;
- reductions are i64-only for this path;
- Embree and non-partner OptiX parity paths are count/sum only;
- no SQL parser or query optimizer is implemented;
- no RayDB storage layout, query plan, or full benchmark workload is
  reproduced;
- no authors-code build or timing is included;
- no true zero-copy wording is authorized because outputs still cross into
  Python-owned materialization;
- no public speedup wording is authorized.

## Authors-Code Comparison

Authors-code performance comparison is a separate goal, not part of Goal2520.

Before any comparison, the next goal must answer:

1. Is the authors' code available locally or in a public repository?
2. Can it be built reproducibly on our machine or pod?
3. Does it expose a benchmark/query matching our same-contract slice under the
   same input/query/result contract?
4. Are inputs, predicates, grouping semantics, result modes, and result
   materialization comparable?
5. Is the comparison against a full RayDB system, a kernel, or a subpath?

If those answers are not all clear, the correct report is "not comparable", not
a forced performance number.

## Closeout Decision

Stop implementation for this RayDB-style benchmark slice here.

Recommended next goal:

`Goal2521`: RayDB authors-code feasibility gate.

Only after Goal2521 succeeds should we attempt authors-code build/timing or
same-contract performance comparison.
