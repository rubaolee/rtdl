# Goal2904: Current Packet After Hausdorff Fix

Date: 2026-05-31
Status: accepted as internal post-fix packet evidence

## Purpose

Goal2904 reruns the current seven-app canonical packet after Goal2903 changed the Hausdorff canonical exact RT path from adaptive radius growth to reduced bbox nearest-witness traversal.

## Pod Packet

Artifact directory:

`docs/reports/goal2904_current_packet_after_hausdorff_fix_pod/`

Summary:

- source commit: `b6cc4591a0d475489a7cdddb9c15d32aa852afbc`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- seven-app canonical packet: `7 / 7` passed
- packet elapsed time: `423.442 s`
- claim-boundary violations: none

## Triage Result

Triage artifact:

`docs/reports/goal2904_current_packet_after_hausdorff_fix_triage_2026-05-31.json`

The previous severe Hausdorff deficit is gone:

- Goal2902 Hausdorff ratio: `19.119x` RTDL/CuPy
- Goal2904 Hausdorff ratio: `1.067x` RTDL/CuPy
- classification: `current_path_acceptable_near_parity`

The only remaining target in this packet is Barnes-Hut, and only because the packet predates Goal2905 measured partner selection:

- OptiX membership speedup vs Embree: up to `157.450x`
- Triton vector sum vs Torch: `4.131x` slower
- classification in this packet: `performance_target`

## Interpretation

This confirms the main v2.5 performance lesson:

- Dense exact Hausdorff should use generic reduced nearest-witness traversal with a conservative bbox radius, not repeated adaptive RT threshold launches.
- Barnes-Hut should not be treated as a native RT problem. The RT membership stage is already strong; the remaining issue is partner selection for grouped vector sums.

## Boundary

This is not release consensus and not a v2.5 release packet.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, package-install claims, automatic Triton selection, or paper reproduction claims.
