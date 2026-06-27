# Goal2942: Current Packet After RayJoin Row-Column Bridge

Date: 2026-06-01
Status: pod packet passed

## Purpose

Goal2942 reruns the full seven-app v2.5 canonical packet after Goal2938,
Goal2939, and Goal2941 added the generic `OptixRowView` to typed partner-column
bridge and measured it on Spatial RayJoin row streams.

The bridge is intentionally narrow:

- RTDL/OptiX still owns the generic RT traversal and row-view production.
- The Python partner layer can convert row-view fields into typed Torch,
  Triton-carrier, or CuPy columns without Python dict row materialization.
- The current implementation remains host-staged and does not claim true
  device-resident zero-copy handoff.
- Count/parity paths remain canonical when the caller does not need rows.

Artifact directory:

`docs/reports/goal2942_current_packet_after_row_columns_pod/`

## Packet Result

- source commit: `74f6c66ef9cb44b0af0cec8c8c67113dffac2831`
- status: `pass`
- all_pass: `true`
- artifact count: `7 / 7`
- dirty artifacts: `{}`
- claim-boundary violations: `{}`
- elapsed: `455.518s`

The packet records Goal2916 toolchain provenance:

- GPU: `NVIDIA RTX A5000, 570.211.01`
- metadata version: `rtdl.goal2916.toolchain_provenance.v1`
- CUDA home: `/usr/local/cuda-12`
- NVCC: CUDA `12.8`
- PTX arch/compiler: `compute_86`, `nvcc`
- Torch/CuPy/Triton/Numba: `2.8.0+cu128`, `14.1.0`, `3.4.0`, `0.65.1`
- RTDL OptiX library exists: `true`
- OptiX header exists: `true`

## Current Triage

`goal2942_triage.json`:

- status: `pass`
- performance targets: `[]`
- top priority: `null`

Key rows:

| App | Status | Key value |
| --- | --- | --- |
| RTNN | `current_path_acceptable` | CuPy/RTDL ratios: min `1.15x`, max `7.64x` |
| Hausdorff/X-HD | `current_path_acceptable_near_parity` | target `4096`, RTDL/CuPy ratio `1.038x`; exact and RTDL/OptiX-backed, but not a speedup claim |
| RT-DBSCAN | `current_path_acceptable` | grouped stream speedup vs prepared CuPy grid `3.854x` to `4.820x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | CuPy selected for vector-sum continuation; max OptiX membership speedup vs Embree `155.800x` |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity path only in canonical packet; row-column scale bridge tracked by Goal2941 |

Barnes-Hut vector continuation:

| Partner | Median seconds | Ratio vs Torch | Selected |
| --- | ---: | ---: | --- |
| Torch scatter-add | `0.000882599` | `1.000x` | no |
| Triton offsets | `0.003482741` | `3.946x` slower | no |
| CuPy by-key | `0.000699970` | `0.793x` | yes |

Spatial RayJoin row-column bridge evidence from Goal2941 remains green:

| Workload | Rows | Count-only median sec | Typed-column median sec | Ratio |
| --- | ---: | ---: | ---: | ---: |
| PIP rows | `4096` | `0.000731917` | `0.001310086` | `1.790x` |
| LSI rows | `65536` | `0.006797644` | `0.008633615` | `1.270x` |
| Overlay seed rows | `262144` | `0.073687353` | `0.074747488` | `1.014x` |

The row-column bridge result is a design confirmation, not a public speedup
claim: once row streams are large, typed partner columns add small overhead
relative to producing the rows; at small row counts, fixed setup cost is still
visible, so count-only should stay canonical when rows are not needed.

## Result

Goal2942 confirms that adding the typed partner-column bridge does not regress
the current seven-app v2.5 packet. It also keeps the next architectural target
honest: this is a useful host-staged bridge for user continuations, while the
larger v2.5-v3.0 roadmap still points toward real device-resident row-stream
handoff and richer event-ordered grouped reductions. In short, device-resident
row-stream handoff is still the next larger runtime target.

The important user-language effect is that RTDL is moving from "RT cores produce
opaque app results" toward "RT cores produce generic primitive payloads that a
Python partner can consume under an explicit contract." The current bridge gives
users a practical typed-column path today; it does not pretend that the v3.0
zero-copy stream is already done.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic Triton-selection
claim, automatic CuPy-selection claim, package-install claim, paper-reproduction
claim, or app-specific native engine logic claim.

Release still requires a user-requested release packet and fresh 3-AI release
consensus.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2942_current_packet_after_row_columns_test tests.goal2941_rayjoin_row_view_partner_columns_scale_probe_test tests.goal2939_rayjoin_row_view_partner_columns_pod_smoke_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 18 tests
OK
```
