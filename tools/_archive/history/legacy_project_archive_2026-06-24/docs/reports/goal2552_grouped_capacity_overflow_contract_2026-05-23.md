# Goal2552: Grouped Capacity Overflow Contract

Date: 2026-05-23
Status: implemented as an internal hardening slice, not a public release

## Context

The Goal2551 three-AI benchmark-app-wave consensus identified a concrete P0
ABI defect in the OptiX partner-resident grouped reduction path: all six
`*_with_capacity` entry points accepted `group_capacity`, but none returned an
`overflowed_out` signal. A caller could not distinguish an exact compact
grouped result from a capacity-hit condition without relying on native error
strings.

This was more urgent than the broader `RtdlDb*` and `DbScan*` rename because it
affects correctness semantics, not just architecture naming. The naming cleanup
remains the next migration slice before any external ABI stabilization.

## Change

The following OptiX capacity-bounded grouped APIs now include
`uint32_t* overflowed_out` after `row_count_out` and before `error_out`:

- `rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_stats_i64_with_capacity`

Native behavior is fail-closed:

- success with exact rows sets `*overflowed_out = 0`;
- dense-group capacity hits set `*overflowed_out = 1`;
- capacity-hit wrappers return no partial rows;
- legacy non-capacity wrappers preserve the previous error behavior.

Python `ctypes` declarations and runtime wrappers now pass the overflow pointer
and raise if the native path reports overflow, so exact row semantics are not
authorized after a capacity hit.

## Boundary

This does not make the grouped partner-resident path a stable public ABI. It is
an internal correctness hardening step for the current benchmark-app research
snapshot. Public wording still requires the existing evidence and consensus
gates.

This also does not complete the app-independent engine cleanup. The broader
`RtdlDb*` and `DbScan*` rename remains open because it touches public struct
names, Python bindings, and legacy tests. That rename should be done as a
separate compatibility/migration slice with explicit source-purity tests.

## Validation

Focused local validation:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2552_grouped_capacity_overflow_contract_test \
  tests.goal2551_benchmark_app_wave_rethinking_consensus_test \
  tests.goal2513_partner_resident_group_capacity_contract_test \
  tests.goal2515_partner_resident_grouped_min_max_i64_test \
  tests.goal2517_partner_resident_fused_sum_count_i64_test \
  tests.goal2527_large_same_contract_performance_matrix_test
```

Result: 31 tests passed locally.

Native GPU validation is still required before treating this ABI revision as
externally consumable.
