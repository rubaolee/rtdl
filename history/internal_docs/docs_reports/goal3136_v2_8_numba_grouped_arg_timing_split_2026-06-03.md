# Goal3136: v2.8 Numba Grouped-Arg Timing Split

Date: 2026-06-03

Status: diagnostic pod timing completed; performance debt localized

## Purpose

Goal3132 proved that the v2.8 partner front door can execute all currently
supported operations on a healthy RTX 4000 Ada pod stack. It also found negative
timing for the Numba `grouped_argmin_f64` and `grouped_argmax_f64` paths.

Goal3136 splits that timing into direct partner-kernel and v2.8 front-door
adapter paths, with validation and compaction toggles, to identify whether the
slowdown is mostly in the v2.8 wrapper or in the current Numba grouped-arg
implementation.

## Pod

User supplied:

```text
ssh root@157.157.221.29 -p 24317 -i ~/.ssh/id_ed25519
```

The pod rejected the default key. The working key was:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\id_ed25519_rtdl_codex
```

Environment:

- host: `4463b4adb79b`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- driver: `580.65.06`
- Python: `3.12.3`
- repo path: `/root/rtdl_v28_goal3132`
- commit: `44dcf249`
- venv: `/root/rtdl_v28_env`
- Numba: `0.65.1`
- CuPy: `14.1.1`
- Torch: `2.12.0+cu130`

Artifact:

`docs/reports/goal3136_pod_artifacts/numba_grouped_arg_timing_split_2026-06-03.json`

## Timing Matrix

All timings are median steady-state seconds over three repetitions. They are
diagnostic timings only, not public speedup evidence.

| Rows | Operation | Direct Default Compact | Front Door Default Compact | Front Door No-Validate Compact | Front Door No-Validate Dense | Default / Dense |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 65,536 | `grouped_argmin_f64` | 0.187352 | 0.195069 | 0.154911 | 0.138641 | 1.407x |
| 65,536 | `grouped_argmax_f64` | 0.194755 | 0.197245 | 0.155891 | 0.140916 | 1.400x |
| 262,144 | `grouped_argmin_f64` | 0.194942 | 0.199414 | 0.155924 | 0.141935 | 1.405x |
| 262,144 | `grouped_argmax_f64` | 0.199848 | 0.201746 | 0.156026 | 0.142743 | 1.413x |
| 1,048,576 | `grouped_argmin_f64` | 0.190911 | 0.190558 | 0.149037 | 0.135133 | 1.410x |
| 1,048,576 | `grouped_argmax_f64` | 0.190768 | 0.190910 | 0.149400 | 0.134883 | 1.415x |

## Interpretation

The v2.8 front-door adapter is not the dominant cost. Direct default compact
timings and front-door default compact timings are close, especially at the
largest size.

The main debt is the current Numba grouped-arg path:

- Validation plus compact-present-groups adds about 40 percent over the dense,
  no-validation mode.
- Even the fastest dense, no-validation mode remains about 0.135-0.143 seconds
  across these sizes.
- Numba emitted under-occupancy warnings at 65K, 262K, and 1M rows; the grid
  sizes were 4, 16, and 64 respectively.
- The implementation still uses a multi-kernel score/item tie-break path plus
  host-visible compaction metadata, so it is not yet the fused resident grouped
  arg primitive v2.8 wants.

## Claim Boundary

This report authorizes no release, public speedup wording, broad RT-core
wording, true-zero-copy wording, hidden dispatch, automatic partner selection,
app-specific native-engine behavior, or user-defined shader injection.

## Next Engineering Target

The next grouped-arg performance target should be a generic optimized grouped
arg primitive or partner path that:

- avoids host compaction when a dense output contract is acceptable;
- keeps validation policy explicit and fail-closed;
- improves occupancy rather than launching only one thread per group-sized
  batch;
- preserves deterministic score-then-item-id tie-break semantics;
- keeps the user-selected partner explicit.
