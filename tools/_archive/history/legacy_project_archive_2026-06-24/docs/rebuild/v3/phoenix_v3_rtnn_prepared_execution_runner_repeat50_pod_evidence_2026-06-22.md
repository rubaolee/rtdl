# Phoenix V3 RTNN Prepared-Execution Runner Repeat50 POD Evidence

Date: 2026-06-22

Status: `accepted_second_set_a_material_probe_not_release`

This packet records focused Phoenix V3 Step-2 runtime-trunk evidence for the generic `fixed_radius_ranked_summary_3d` prepared-execution runner. It is not V3 release authorization, not an all-app benchmark, not a broad V3-over-V2 claim, not a whole RTNN paper claim, and not a true zero-copy or embedding claim.

## Evidence Paths

- Local summary: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/summary.json`
- Local README: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/README.md`
- Local payloads:
  - `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/productized_prepared_execution_runner.json`
  - `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/legacy_app_front_door_prepared_optix.json`
  - `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/cupy_grid_reference.json`
- POD path: `/root/rtdl_v3_rebuild_20260620/current/docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622`
- Local stdout log: `docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622_local_logs/stdout.log`

## Preconditions

- Pre-pod second-AI review: `docs/reviews/kepler_phoenix_v3_rtnn_step2_pre_pod_review_2026-06-22.md`
- Verdict: `accept_for_pod`
- Local focused gates: `29 tests OK`
- POD focused gates: `29 tests OK`
- POD smoke: 1,024 points, repeat2, `runtime_trunk_executes_end_to_end=true`, `repeat50_material_probe_candidate=false`, runner/legacy signatures matched exactly.
- Result-level second-AI review: `docs/reviews/kepler_phoenix_v3_rtnn_step2_result_review_2026-06-22.md`
- Result verdict: `accept_as_second_set_a_material_probe`

## Serious POD Configuration

- Hardware: same RT-capable POD route used for Phoenix evidence.
- Point count: `1,048,576`
- Distribution: `uniform`
- Radius: `0.02`
- K: `50`
- Repeat: `50`
- Warmups: `3`
- Routes:
  - `productized_prepared_execution_runner`
  - `legacy_app_front_door_prepared_optix`
  - `cupy_grid_reference`

## Correctness And Parity

Runner vs legacy OptiX app-front-door:

- Row count delta: `0`
- Bounded-neighbor count delta: `0`
- Nearest-id checksum delta: `0`
- Kth-id checksum delta: `0`
- Sum-distance relative error: `2.160265046994547e-16`
- Signature match: `true`

Runner vs CuPy grid reference:

- Row count delta: `0`
- Bounded-neighbor count delta: `0`
- Nearest-id checksum delta: `0`
- Kth-id checksum delta: `0`
- Sum-distance relative error: `3.071810486130005e-11`
- Signature match: `true`

## Runtime-Trunk Result

The productized runner reported:

- `productized_execution_path=prepared_execution_session_runner`
- `runtime_trunk_executes_end_to_end=true`
- `internal_device_residency_between_rtdl_phases=true`
- `repeat50_material_probe_candidate=true`
- `runtime_sourced_material_gain_candidate=true`

This is a material focused result for the runtime trunk, because the same generic prepared-execution runner now executes a second Set-A family end to end after the Barnes-Hut runner evidence. The result-level review authorizes moving to a third Set-A focused probe, not all-app or release.

## Timing Results

| route | hot query median | cold-plus-query wall | runner wall |
|---|---:|---:|---:|
| productized prepared-execution runner | `0.010809954s` | `1.778338227s` | `2.341840900s` |
| legacy app-front-door prepared OptiX | `0.010688677s` | `2.415568337s` | `3.208734035s` |
| CuPy grid reference | `0.084176254s` | `2.010270018s` | `7.485395484s` |

Comparisons:

- Runner over CuPy hot query: `7.786920x`
- Runner over CuPy cold-plus-query: `1.130421x`
- Runner over CuPy runner-wall: `3.196372x`
- Runner vs legacy hot query: `0.988781x`
- Runner vs legacy cold-plus-query: `1.358329x`
- Runner vs legacy runner-wall: `1.370176x`

Interpretation: hot query speed remains the strongest signal. The more important Phoenix V3 result is that the productized runner preserved correctness, proved internal residency through returned runtime metadata, and improved cold/runner-wall versus the legacy app-front-door route while staying on a generic runtime trunk.

## Non-Authorization

The summary keeps all release/public/global flags false:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

## Goal-Level Decision Audit

1. Was I foolish? No. The run followed the corrected sequence: local gates, second-AI pre-pod review, smoke, then focused serious POD evidence.
2. If yes, what actions made it foolish? The previous foolish pattern would have been to count the old RTNN repeat50 row as V3 runtime-trunk evidence without routing it through the productized runner.
3. Was there another path? Yes: rerun all-app or cache-hygiene work. That would still avoid proving shared runtime machinery.
4. Can I now try a different path that actually solves the problem? Yes. Send this exact result for 2-AI result review; if accepted, proceed to a third Set-A family before any all-app rerun.
