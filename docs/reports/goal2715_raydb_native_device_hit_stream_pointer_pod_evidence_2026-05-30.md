# Goal2715: RayDB Native Device Hit-Stream Pointer Evidence on RTX A5000

Date: 2026-05-30
Status: accepted as pod evidence with claim boundary

## Purpose

This goal closes the specific evidence gap raised by the v2.5 reviews: the RayDB-style v2.5 path must prove that native OptiX device hit-stream columns can feed the Torch/Triton carrier without first materializing host hit rows, and that the CUDA-array-interface/DLPack carrier preserves the same device pointer at execution time.

This is not a public speedup claim and not a final true-zero-copy authorization. It is a hardware evidence milestone for the internal v2.5 device-column handoff contract.

## Artifacts

- Full grid: `docs/reports/goal2715_pod_artifacts/goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.json`
- Full grid log: `docs/reports/goal2715_pod_artifacts/goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.log`
- Metadata cleanup smoke: `docs/reports/goal2716_pod_artifacts/goal2716_hit_stream_carrier_execution_flag_smoke_pod_69_30_85_171_2026-05-30.json`
- Pod: `69.30.85.171:22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`

## Commits

- Full 30-case grid: `53016a58ea5c8d16e33c34ecac0faa3400aae079`
- Follow-up metadata cleanup smoke: `3224d405286149af2c3aad738cd87f834dbf7db0`

The follow-up commit changed only the execution-evidence flag semantics: the planning adapter still reports `adapter_execution_proven_on_hardware = false`, while the executed carrier metadata reports it as true only when CUDA execution observes same-pointer carrier input. The public gates remain false.

## Evidence Summary

The full grid ran 30 cases: 3 row counts x 5 reduction modes x 2 RayDB paths. All cases matched the CPU reference.

For all 15 native-device-column cases:

- `native_device_column_path_used = true`
- `host_row_bridge_bypassed = true`
- `handoff_materializes_host_rows_for_bridge = false`
- `torch_carrier_execution.same_pointer_evidence_observed = true`
- `primitive_ids_same_pointer_as_input = true`
- `primitive_group_ids_same_pointer_as_input = true`
- `primitive_values_same_pointer_as_input = true`
- `true_zero_copy_authorized = false`
- `no_public_speedup_claim = true`

The follow-up smoke at `3224d405` additionally proves:

- `torch_carrier_execution.adapter_execution_proven_on_hardware = true`
- `torch_carrier_execution.same_pointer_evidence_observed = true`
- `true_zero_copy_authorized = false`

## Full Grid Wall-Clock Results

Ratio is native-device-column median divided by host-bridge median. Values below 1.0 mean the native-device-column path was faster for that case.

| rows | mode | host bridge median s | native device median s | device/host |
| ---: | --- | ---: | ---: | ---: |
| 10000 | count | 0.027361 | 0.026493 | 0.968x |
| 10000 | sum | 0.094127 | 0.090201 | 0.958x |
| 10000 | min | 0.093055 | 0.094718 | 1.018x |
| 10000 | max | 0.091295 | 0.184413 | 2.020x |
| 10000 | avg_as_sum_count | 0.092968 | 0.096542 | 1.038x |
| 100000 | count | 0.220351 | 0.227156 | 1.031x |
| 100000 | sum | 0.677729 | 0.690914 | 1.019x |
| 100000 | min | 0.790382 | 0.704805 | 0.892x |
| 100000 | max | 0.696483 | 0.887735 | 1.275x |
| 100000 | avg_as_sum_count | 0.671929 | 0.578954 | 0.862x |
| 1000000 | count | 1.793550 | 1.884029 | 1.050x |
| 1000000 | sum | 2.217291 | 2.220117 | 1.001x |
| 1000000 | min | 2.660070 | 2.275859 | 0.856x |
| 1000000 | max | 2.208814 | 2.239246 | 1.014x |
| 1000000 | avg_as_sum_count | 2.171307 | 2.664585 | 1.227x |

## Device-Path Phase Medians

| rows | workload build s | RT hit stream total s | RT traversal s | native call s | column handoff s | typed gather s | Triton continuation s | total metadata elapsed s |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10000 | 0.049218 | 0.017860 | 0.000191 | 0.016915 | 0.003318 | 0.000595 | 0.006752 | 0.077047 |
| 100000 | 0.294912 | 0.142002 | 0.000676 | 0.136730 | 0.014608 | 0.000782 | 0.004821 | 0.484068 |
| 1000000 | 0.474237 | 0.164899 | 0.001218 | 0.129725 | 0.175034 | 0.000655 | 0.005523 | 0.821249 |

## Interpretation

The important win is structural, not a broad speedup headline:

1. The native OptiX path now emits device hit-stream columns that bypass host hit-row construction.
2. The Torch/Triton carrier adapter executed on an RTX A5000 and preserved the same pointers for the raw CUDA-array primitive-id column and the Torch payload columns.
3. The v2.4 phase metadata now records nonzero RT traversal time for the device path instead of losing it under a label mismatch.

The wall-clock results are mixed. Some reductions are faster, some are near parity, and some are slower. That is expected at this stage because the full workload still includes workload construction, native owner setup, column-handoff overhead, and partner-continuation launch costs. The evidence supports "host row bridge removed for this path" and "same-pointer carrier execution observed"; it does not support a broad speedup claim.

## Boundary

Still blocked:

- No public true-zero-copy claim.
- No public whole-app speedup claim.
- No claim that Triton should be forced onto all benchmark apps.
- No claim that all v2.5 benchmark apps are ready; the benchmark suite remains tiered by continuation shape.

Next useful work:

1. Reduce `hit_stream_column_handoff` / native-owner setup overhead at 1M rows.
2. Separate cold workload-build cost from steady-state prepared-table reuse in the RayDB runner.
3. Add a neutral partner carrier path that does not make Torch the only practical carrier.
4. Extend the same evidence pattern to Tier A apps whose continuation shape matches grouped scalar reductions.
