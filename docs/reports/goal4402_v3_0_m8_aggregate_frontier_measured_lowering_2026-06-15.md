# V3.0 M8 Aggregate-Frontier Measured Lowering

Date: 2026-06-15

Status: measured native lowering pilot passed; no public acceleration claim.

## Result

M8 adds the first V3.0 measured lowering pilot over an existing app-generic native ABI:
`generic_aggregate_frontier_collect_2d_native_abi_v1`.

The pilot was run on the pod at commit `7c2585a1` with:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20475 MiB
- Native OptiX symbol: `rtdl_optix_collect_aggregate_frontier_2d`
- Native Embree symbol: `rtdl_embree_collect_aggregate_frontier_2d`
- Tests: `tests.goal4402_v3_0_m8_measured_lowering_test` passed on pod

## Perf Matrix

| Point Count | Frontier Rows | Embree Median | OptiX Median | Ratio, Embree/OptiX | Winner |
| ---: | ---: | ---: | ---: | ---: | --- |
| 512 | 56,034 | 0.115432s | 0.113482s | 1.017x | OptiX by noise-level margin |
| 2,048 | 523,035 | 1.121130s | 1.103184s | 1.016x | OptiX by noise-level margin |
| 4,096 | 2,709,984 | 6.026181s | 6.022993s | 1.001x | Tie |

Raw evidence:

- `docs/reports/goal4402_v3_0_m8_aggregate_frontier_lowering_512_2026-06-15.json`
- `docs/reports/goal4402_v3_0_m8_aggregate_frontier_lowering_2048_2026-06-15.json`
- `docs/reports/goal4402_v3_0_m8_aggregate_frontier_lowering_4096_2026-06-15.json`

## Interpretation

This is an important engineering pass, but not a speedup result. The V3 harness now executes a real native lowering path for both Embree and OptiX, checks same-contract parity against the CPU reference, records phase-complete instrumentation, and packages the rows through the V3 benchmark harness. That is the first step from V3 design into measured execution.

The OptiX-vs-Embree result is essentially tied because this aggregate-frontier symbol is a generic row collector that returns host-materialized rows. Its own claim boundary says it is not RT-core traversal speedup evidence. The measured payload correctly reports:

- `device_resident_ready = false`
- `true_zero_copy_ready = false`
- `public_claim_authorized = false`
- `rt_core_speedup_claim_authorized = false`

## What Passed

1. Same-contract parity passed for Embree and OptiX at all tested scales.
2. The V3 M7 harness accepted paired `rtdl_embree` and `rtdl_optix` rows with the same contract key.
3. The V3 M3 instrumentation packets are phase-complete.
4. The claim boundary remained locked.
5. The larger 4,096-point case reached a 6-second native-lowering measurement, so this is no longer a millisecond toy-only probe.

## What Remains

The next gate must target a device-resident primitive plus partner continuation. M8 proves that V3 can wrap a real native ABI honestly; it does not yet prove V3 can keep streams resident across RT traversal and continuation. The next measured pilot should require:

- device-resident output or backend-native handle evidence
- no host row materialization between primitive and continuation
- CuPy and Numba partner rows when a partner is needed
- separated traversal, handoff, continuation, and materialization timing
- no public speedup wording until a benchmark-app-scale comparison passes
