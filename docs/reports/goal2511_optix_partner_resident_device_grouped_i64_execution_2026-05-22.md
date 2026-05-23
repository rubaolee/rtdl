# Goal2511 OptiX Partner-Resident Device Grouped I64 Execution

Date: 2026-05-22

## Summary

Goal2511 adds the first experimental-only executable partner-resident columnar path
for the OptiX backend. It is intentionally narrow and explicitly gated from
public use.

New native symbols:

- `rtdl_optix_columnar_device_payload_grouped_count_i64`
- `rtdl_optix_columnar_device_payload_grouped_sum_i64`

New Python entry points:

- `run_optix_partner_resident_columnar_grouped_count_i64(...)`
- `run_optix_partner_resident_columnar_grouped_sum_i64(...)`

These entry points require `allow_experimental_native=True`.

## Executable Scope

This slice supports:

- partner-resident CUDA numeric columns described by `RtdlDevicePayloadField`
- numeric predicates
- exactly one int64-compatible group key
- grouped count
- grouped int64-compatible sum
- device-side predicate evaluation
- device-side grouped count/sum reduction
- host materialization of only compact grouped result rows

The device kernel uses dense group workspaces and therefore requires dense
non-negative group keys below the configured group capacity. Goal2511 used the
legacy default capacity; Goal2513 adds explicit capacity control for compact
workspace sizing.

## What It Still Does Not Do

This is not the full RayDB-style target yet:

- no SQL or DBMS interface
- no text columns
- no min/max/avg
- no arbitrary int64 group-key hash table
- no RT-core traversal or prepared OptiX DB dataset integration
- no public speedup or true-zero-copy claim

No speedup or zero-copy claim is authorized.

## Claim Boundary

Allowed wording:

- RTDL has an experimental OptiX CUDA execution slice for partner-resident
  numeric column descriptors.
- The slice validates no-hidden-input-table-copy execution for dense grouped
  count/sum cases.

Forbidden wording:

- RTDL has complete partner-resident RayDB-style execution.
- RTDL has zero-copy database execution.
- RTDL has a SQL/DBMS engine.
- RTDL has public RayDB speedups.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2511_optix_partner_resident_device_grouped_i64_execution_test
```

Expected result:

```text
6 tests OK
```

RayDB-style local sequence through Goal2511:

```text
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
  tests.goal2511_optix_partner_resident_device_grouped_i64_execution_test
```

Result:

```text
102 tests OK, 4 skipped
```

Pod-focused ABI/probe validation:

```text
PYTHONPATH=/root/rtdl_python_only_goal2501/src:/root/rtdl_python_only_goal2501 \
RTDL_OPTIX_LIB=/root/rtdl_python_only_goal2501/build/librtdl_optix.so \
python3 -m unittest \
  tests.goal2507_optix_device_column_abi_scaffold_test \
  tests.goal2508_optix_partner_resident_python_scaffold_test \
  tests.goal2509_optix_partner_resident_scaffold_pod_probe_packet_test \
  tests.goal2510_optix_device_column_abi_validation_test \
  tests.goal2511_optix_partner_resident_device_grouped_i64_execution_test
```

Result:

```text
21 tests OK
```

## Pod Evidence

Pod SSH used:

```text
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519_rtdl_codex -p 22017 root@69.30.85.198
```

Build evidence:

- remote checkout: `/root/rtdl_python_only_goal2501`
- OptiX headers: `/root/vendor/optix-dev-9.0.0`
- CUDA prefix: `/usr/local/cuda`
- build log: `docs/reports/goal2511_make_build_optix_2026-05-22.txt`
- result: `make build-optix` completed successfully with only the CUDA
  deprecated-target warning.

Probe evidence:

- artifact: `docs/reports/goal2511_optix_partner_resident_device_grouped_i64_pod_2026-05-22.json`
- platform: `Linux-5.15.0-107-generic-x86_64-with-glibc2.39`
- Python: `3.12.3`
- PyTorch: `2.8.0+cu128`
- CUDA available: `true`
- descriptor device: `cuda:0`
- descriptor source protocol: `torch`
- status: `ok`
- count_matches_cpu: true
- sum_matches_cpu: true

Observed grouped outputs matched the CPU oracle for the synthetic RayDB-style
fixture:

- count: `[{region_id: 0, count: 2}, {region_id: 1, count: 1}, {region_id: 2, count: 1}]`
- sum: `[{region_id: 0, sum: 190}, {region_id: 1, sum: 200}, {region_id: 2, sum: 80}]`

The probe still records `true_zero_copy_authorized: false`. The evidence is
only that the input table stayed partner-resident as CUDA tensor descriptors
for this narrow grouped count/sum slice, while compact grouped result rows were
materialized back to host/Python.
