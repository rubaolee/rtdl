# Goal2327 RayJoin Performance Tuning Round 1

Date: 2026-05-18

Status: `local-prep-complete-pod-needed`

## Purpose

RayJoin is the benchmark application for the next v2.0 performance push. The
goal is to pursue the six concrete gaps identified after the Goal2315 closure
without violating the RTDL rule that native engines remain app-agnostic.

## Six Work Tracks

| Track | Goal | Local status | Pod needed |
| --- | --- | --- | --- |
| 1. Generic device-resident row stream / continuation | Let prepared primitives feed downstream count/reduction/continuation without host row materialization | Design boundary recorded; RayJoin app now exposes the missing status explicitly | yes |
| 2. Generic grouped count/parity reduction | Support RayJoin-style count/parity over generic row streams | Existing partner reductions are identified as the CPU/GPU partner layer; native continuation still pending | yes |
| 3. Stronger prepared closed-shape membership | Use the accepted point/closed-shape primitive for PIP-like joins instead of boundary-segment grouping | Exposed through the benchmark app's prepared OptiX route | yes for timing |
| 4. Many-query batching and launch grouping | Separate one-time pack/prepare from warm query repeats and compare repeated-call behavior | Prepared route and pod runner use warmups/repeats; same-query stream replay remains available | yes |
| 5. Phase-separated timing | Report pack, static scene prepare, prepared query, and native phase telemetry separately | Implemented in `run_rayjoin_prepared_optix_workload(...)` | yes for OptiX data |
| 6. Paper-protocol reproduction discipline | Keep RayJoin query phase, RTDL prepared query phase, full Python call, and whole-app command separate | Pod runner reuses the existing same-query stream harness and keeps claim boundaries locked | yes |

## Local Implementation

`examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
now supports:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --execution-route prepared_optix --result-mode count --no-rows
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload pip --execution-route prepared_optix --result-mode rows --no-rows
```

The route reports:

- `phases_sec.query_pack_sec`
- `phases_sec.static_shape_pack_sec` for PIP
- `phases_sec.prepare_static_scene_sec`
- `phases_sec.prepared_query_sec`
- `native_phase_timings` when the OptiX runtime supplies them
- `device_resident_continuation_status`
- locked claim-boundary flags

Overlay remains deliberately excluded from `prepared_optix` for now. It needs a
generic device-resident continuation or dependency-row stream, not an
overlay-specific native shortcut.

## Pod Runner

Added:

```bash
scripts/goal2327_rayjoin_pod_perf_runner.sh
```

It prints progress for every step, enforces `STEP_TIMEOUT_SECONDS`, records GPU
identity, runs fixture PIP/LSI prepared-route probes, and optionally replays
RayJoin-exported same-query streams through
`scripts/goal2292_rayjoin_current_prepared_comparison.py` when `LSI_STREAM` and
`PIP_STREAM` are supplied. It then writes a compact human-readable
`summary.md` through `scripts/goal2327_rayjoin_pod_artifact_summary.py` so the
pod output can be reviewed without manually opening every JSON artifact.

## Claim Boundary

This round does not claim:

- RTDL beats RayJoin;
- full RayJoin paper reproduction;
- broad RT-core speedup;
- whole-application speedup;
- true zero-copy;
- v2.0 release authorization.

The next pod run is required before any performance conclusion changes.

## External Review

Gemini reviewed the Goal2327 packet in
`docs/reviews/goal2328_gemini_review_goal2327_rayjoin_perf_tuning_round1_2026-05-18.md`
and returned `accept-with-boundary`. The review agrees that the PIP/LSI prepared
route advances the RayJoin performance lane while keeping native engines
app-agnostic and claim boundaries locked. It also agrees that overlay remains a
documented gap until a generic device-resident continuation exists.

## Local Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2327_rayjoin_prepared_route_contract_test tests.goal2327_rayjoin_perf_tuning_packet_test tests.goal2326_public_primitive_contract_test tests.goal2326_execution_report_contract_test
$env:PYTHONPATH='src;.'; py -3 -m compileall -q examples\v2_0\research_benchmarks\spatial_rayjoin tests\goal2327_rayjoin_prepared_route_contract_test.py tests\goal2327_rayjoin_perf_tuning_packet_test.py
```

Result: 14 focused tests pass and compileall passes.
