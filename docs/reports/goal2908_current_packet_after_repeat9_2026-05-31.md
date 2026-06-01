# Goal2908: Current Packet After Hausdorff Repeat-9 Default

Date: 2026-05-31
Status: accepted as internal current-packet evidence

## Purpose

Goal2908 reruns the seven-app v2.5 canonical packet after Goal2907 changed the Hausdorff canonical entrypoint default from repeat 3 to repeat 9.

## Pod Packet

Artifact directory:

`docs/reports/goal2908_current_packet_after_repeat9_pod/`

Summary:

- source commit: `f101b4da0fa088c76ed30711e5b32b1984a411da`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- seven-app canonical packet: `7 / 7` passed
- packet elapsed time: `440.973 s`
- claim-boundary violations: none
- dirty artifacts: none

## Triage Result

Triage artifact:

`docs/reports/goal2908_current_packet_after_repeat9_triage_2026-05-31.json`

The Hausdorff target is closed in this packet:

- CuPy grid median: `0.004491 s`
- RTDL/OptiX median: `0.004461 s`
- RTDL/CuPy ratio: `0.993x`
- classification: `current_path_acceptable`

Barnes-Hut remains acceptable through explicit measured partner selection:

- selected vector-sum partner: `torch`
- Triton/Torch vector-sum ratio: `4.338x`
- OptiX membership speedup vs Embree: up to `156.096x`
- classification: `current_path_acceptable_with_measured_partner_selection`

RTNN is the only target in this packet:

- weakest packet row: `clustered`, `0.945x` CuPy/RTDL
- packet classification: `performance_target`

Goal2909 immediately probes that RTNN row with repeat-9 timing on the same input and shows the packet value was another short-row timing artifact rather than a missing primitive.

## Boundary

This is not release consensus and not a v2.5 release packet.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, automatic Triton selection, package-install claims, or paper-reproduction claims.
