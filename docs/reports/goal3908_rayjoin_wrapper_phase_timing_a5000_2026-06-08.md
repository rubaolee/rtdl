# Goal3908 RayJoin Wrapper Phase Timing A5000 Evidence

## Purpose

Goal3908 runs the Goal3907-instrumented RayJoin representative profile on the
A5000 pod to identify where the wrapper time goes.

This is a focused RayJoin run, not a full ten-app packet.

## Environment

- Pod: `ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`
- Fresh pod clone: `/root/goal3908_rayjoin_wrapper_phase_1780903131`
- Source commit: `fe4f3a4b`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Artifact:
  `docs/reports/goal3908_rayjoin_wrapper_phase_timing_a5000/rayjoin_wrapper_phase_profile.json`

The focused command completed with `exit_code = 0`.

## Wrapper Breakdown

| Phase | Seconds | Share of wrapper |
| --- | ---: | ---: |
| `data_dir_resolve_sec` | `0.000113` | `0.0%` |
| `pip_one_shot_probe_sec` | `2.918666` | `30.5%` |
| `lsi_overlay_probe_sec` | `6.129975` | `64.1%` |
| `pip_batch_probe_sec` | `0.513930` | `5.4%` |
| `profile_total_sec` | `9.562869` | `100.0%` |

The largest wrapper cost is the LSI/overlay probe wrapper, followed by the PIP
one-shot probe wrapper. The prepared PIP batch executor is not the wrapper
problem in this run.

## Hot Contract Metrics

| Contract | Numba hot median sec | RTDL/OptiX hot median sec | RTDL/OptiX vs Numba | Current route |
| --- | ---: | ---: | ---: | --- |
| PIP one-shot | `0.000533` | `0.002232` | `0.239x` | Numba |
| LSI scalar count | `0.020732` | `0.000099` | `209.163x` | RTDL/OptiX |
| Overlay active count | `0.048807` | `0.000205` | `238.474x` | RTDL/OptiX |
| PIP repeated requests | `0.216296 ms/request` single | `0.024277 ms/request` batched | `8.909x` | RTDL/OptiX batch |

All contract counts matched.

## Interpretation

The next RayJoin engineering target is not the fused RTDL/OptiX scalar-count
hot path. It is the wrapper/sub-probe setup path, especially the LSI/overlay
reference/probe wrapper. A useful follow-up should reduce duplicate data loading/staging or split the representative profile so each contract's wrapper cost is measured and cached independently.

## Boundary

Goal3908 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is internal RayJoin wrapper diagnostics, not a public performance comparison and not a release packet.
