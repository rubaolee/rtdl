# Goal3757 Robot Collision Scaled Prepared Performance Packet

Date: 2026-06-07

## Purpose

The v2.9 adequacy ledger still described robot collision as a near-parity row.
That was too pessimistic for the correct prepared repeated-query contract. The
full matrix timed out at 1024 poses because it mixed slow/reference rows, so
Goal3757 measures the promoted prepared modes directly and records the contract
split.

## A5000 Evidence

Artifact: `docs/reports/goal3757_robot_collision_scale_probe_a5000/summary.json`

All rows use the deterministic scaled robot-collision fixture with 3 links per
pose, 9 probe segments per link group, 9 repeats, and 2 warmup rows. Each row
matched the probe reference.

| Pose count | Obstacles | Segments | Mode | Tail median sec | Speedup vs Embree prepared buffers |
| ---: | ---: | ---: | --- | ---: | ---: |
| 1024 | 128 | 27648 | Embree prepared buffers | 0.001875968 | 1.000x |
| 1024 | 128 | 27648 | OptiX prepared buffers | 0.001202627 | 1.560x |
| 1024 | 128 | 27648 | OptiX prepared device buffers | 0.000388764 | 4.825x |
| 1024 | 128 | 27648 | OptiX prepared device count | 0.000059850 | 31.345x |
| 4096 | 256 | 110592 | Embree prepared buffers | 0.006223137 | 1.000x |
| 4096 | 256 | 110592 | OptiX prepared device buffers | 0.001571526 | 3.960x |
| 4096 | 256 | 110592 | OptiX prepared device count | 0.000093453 | 66.591x |

## Interpretation

Robot collision is not a weak near-parity app on the promoted prepared
subpath. The right reading is:

- compact collision flags: strong, about 4x faster than Embree at large scale;
- scalar flagged-group count: very strong, 31x-66x faster than Embree;
- whole robot-planning acceleration: not claimed;
- exact solid/continuous collision: not claimed.

The huge count-path win comes from avoiding Python materialization of compact
group flags and returning only a scalar count from the native prepared query.
The compact-flag path is still fast, but its output postprocessing is the main
remaining cost at 4096 poses.

## Boundary

This packet is an internal performance clarification. It does not authorize
release action, public speedup wording, whole-app acceleration wording, broad
RT-core wording, exact solid-collision wording, paper reproduction wording, AMD
performance wording, or app-specific native engine logic.

The result is a prepared repeated-query subpath result, not whole
robot-planning acceleration.

## Validation

Pod timing collection used explicit per-mode commands rather than the full
matrix, because the full matrix mixes slow/reference rows and timed out at
1024 poses. Each timing command wrote JSON to
`docs/reports/goal3757_robot_collision_scale_probe_a5000/` and used a bounded
`timeout`.

Local Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3757_robot_collision_scaled_prepared_perf_packet_test tests.goal3740_benchmark_app_adequacy_after_goal3737_test tests.goal3747_numba_reference_adequacy_closure_test
py -3 -m py_compile src\rtdsl\v2_9_benchmark_adequacy.py tests\goal3757_robot_collision_scaled_prepared_perf_packet_test.py tests\goal3747_numba_reference_adequacy_closure_test.py
```

Current A5000 pod:

```bash
cd /root/rtdl_goal3737_clean
source /root/rtdl_numba_venv/bin/activate
export PYTHONPATH=src:.
timeout 120 python -m unittest tests.goal3757_robot_collision_scaled_prepared_perf_packet_test tests.goal3740_benchmark_app_adequacy_after_goal3737_test tests.goal3747_numba_reference_adequacy_closure_test
timeout 60 python -m py_compile src/rtdsl/v2_9_benchmark_adequacy.py tests/goal3757_robot_collision_scaled_prepared_perf_packet_test.py tests/goal3747_numba_reference_adequacy_closure_test.py
```

All focused checks passed.
