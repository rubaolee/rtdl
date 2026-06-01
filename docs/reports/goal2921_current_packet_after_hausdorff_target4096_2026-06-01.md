# Goal2921: Current Packet After Hausdorff Target 4096

Date: 2026-06-01
Status: pod packet passed

## Purpose

Goal2921 reruns the full seven-app v2.5 canonical packet after Goal2920 changed
the Hausdorff/X-HD canonical reduced grouped witness target from `2048` to
`4096`.

Artifact directory:

`docs/reports/goal2921_current_packet_after_hd4096_pod/`

## Packet Result

- source commit: `fe628f4faec8e7d43521f11afd395b29462fba8b`
- status: `pass`
- all_pass: `true`
- artifact count: `7 / 7`
- dirty artifacts: `{}`
- claim-boundary violations: `{}`
- elapsed: `446.894s`

The packet still records Goal2916 toolchain provenance:

- metadata version: `rtdl.goal2916.toolchain_provenance.v1`
- PTX arch/compiler: `compute_86`, `nvcc`
- RTDL OptiX library exists: `true`
- OptiX header exists: `true`

## Current Triage

`goal2921_triage.json`:

- status: `pass`
- performance targets: `[]`
- top priority: `null`

Key rows:

| App | Status | Key value |
| --- | --- | --- |
| RTNN | `current_path_acceptable` | CuPy/RTDL ratios: uniform `1.053x`, clustered `2.520x`, shell `7.477x` |
| Hausdorff/X-HD | `current_path_acceptable` | target `4096`, RTDL/CuPy ratio `0.915x` |
| RT-DBSCAN | `current_path_acceptable` | grouped stream speedup vs prepared CuPy grid `3.877x` to `5.184x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | Torch selected; max OptiX membership speedup vs Embree `128.846x` |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity path only |

## Result

The prior Hausdorff near-parity risk is improved in the canonical packet. The
new default remains exact, uses RTDL/OptiX, uses RT cores, and does not change
native engine logic.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic Triton-selection
claim, package-install claim, or paper-reproduction claim.

Compiler fairness and second-architecture or multivendor evidence remain
separate release-packet cautions.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2921_current_packet_after_hausdorff_target4096_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 9 tests
OK
```
