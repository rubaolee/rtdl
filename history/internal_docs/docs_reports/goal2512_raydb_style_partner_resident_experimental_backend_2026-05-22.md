# Goal2512 RayDB-Style Partner-Resident Experimental Backend

Date: 2026-05-22

## Summary

Goal2512 integrates the Goal2511 native device grouped-i64 slice into the
RayDB-style benchmark app as an explicit opt-in backend:

```text
optix_partner_resident_experimental
```

The backend is not part of the default diagnostic matrix. Users must request it
explicitly because it requires PyTorch CUDA tensors, the current OptiX backend,
and the experimental native execution flag.

## What Changed

- The RayDB-style app can now run grouped `count` and grouped `sum` through
  CUDA tensor descriptors.
- The app keeps schema, fixture construction, and query meaning in Python.
- RTDL receives generic partner-resident column descriptors and a generic
  grouped count/sum query.
- The backend matrix accepts the experimental backend only when explicitly
  requested.
- `plan_columnar_aggregate_lowering(...)` records a separate experimental
  partner-resident lowering path.

## Claim Boundary

Allowed internal wording:

- The RayDB-style reconstruction harness has an experimental
  Python+partner+RTDL backend for partner-resident CUDA numeric columns.
- The backend validates grouped `count` and grouped `sum` parity when PyTorch
  CUDA and the current OptiX library are available.

Blocked wording:

- No RayDB reproduction.
- SQL engine or DBMS support.
- Authors-code comparison.
- true zero-copy claim.
- Whole-app acceleration claim.
- Public speedup claim.

The fixture still constructs CUDA tensors from Python data. The important
runtime boundary is narrower: after tensor construction, the experimental
native path consumes partner-resident CUDA column descriptors and returns only
compact grouped rows.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2512_raydb_style_partner_resident_experimental_backend_test
```

Expected result:

```text
6 tests OK
```

RayDB-style local sequence through Goal2512:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2493_raydb_code_intake_test tests.goal2494_raydb_style_contract_design_test tests.goal2495_raydb_style_cpu_reference_fixture_test tests.goal2496_raydb_style_embree_lowering_decision_test tests.goal2497_raydb_style_embree_count_sum_parity_test tests.goal2498_raydb_style_optix_count_sum_parity_test tests.goal2499_raydb_style_lowering_plan_test tests.goal2500_raydb_style_backend_matrix_runner_test tests.goal2501_raydb_style_optix_pod_packet_test tests.goal2501_raydb_style_optix_pod_results_test tests.goal2502_raydb_style_benchmark_slice_closeout_test tests.goal2503_direct_columnar_record_set_preparation_test tests.goal2504_columnar_typed_host_buffer_handoff_test tests.goal2505_partner_resident_columnar_descriptor_contract_test tests.goal2506_optix_partner_resident_native_execution_boundary_test tests.goal2507_optix_device_column_abi_scaffold_test tests.goal2508_optix_partner_resident_python_scaffold_test tests.goal2509_optix_partner_resident_scaffold_pod_probe_packet_test tests.goal2510_optix_device_column_abi_validation_test tests.goal2511_optix_partner_resident_device_grouped_i64_execution_test tests.goal2512_raydb_style_partner_resident_experimental_backend_test
```

Result:

```text
108 tests OK, 4 skipped
```

## Pod Evidence

Pod SSH used:

```text
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519_rtdl_codex -p 22017 root@69.30.85.198
```

The pod runner is:

```text
scripts/goal2512_raydb_style_partner_resident_backend_pod.py
```

It must be run with:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=build/librtdl_optix.so python3 scripts/goal2512_raydb_style_partner_resident_backend_pod.py
```

Expected artifact:

```text
docs/reports/goal2512_raydb_style_partner_resident_backend_pod_2026-05-22.json
```

Observed artifact summary:

- status: `ok`
- backend: `optix_partner_resident_experimental`
- CUDA available: `true`
- PyTorch: `2.8.0+cu128`
- suite all_match_cpu_reference: true
- matrix all_match_cpu_reference: true
- suite group_capacity: `3`
- count rows: `[{region_id: 0, count: 2}, {region_id: 1, count: 1}, {region_id: 2, count: 1}]`
- sum rows: `[{region_id: 0, sum: 190}, {region_id: 1, sum: 200}, {region_id: 2, sum: 80}]`

Pod-focused validation after syncing the final source/report/test slice:

```text
16 tests OK
```

Diagnostic matrix medians from this tiny fixture were about 0.94 ms for count
and 0.91 ms for sum. These timings are engineering diagnostics only and do not
authorize public speedup wording.
