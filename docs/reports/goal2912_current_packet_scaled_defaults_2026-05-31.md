# Goal2912: Current Packet with Scale-Stable Defaults

Date: 2026-05-31
Status: accepted as current internal v2.5 performance packet

## Purpose

Goal2912 reruns the seven-app v2.5 canonical packet after Goal2911 moved the short benchmark rows to scale-stable defaults:

- RTNN: `65,536` points, repeat `9`
- Hausdorff/X-HD: `8,192 x 8,192` points, repeat `9`

The purpose is to verify that the current source tree has no active internal performance target after the recent Hausdorff, Barnes-Hut, and RTNN fixes.

## Pod Packet

Artifact directory:

`docs/reports/goal2912_current_packet_scaled_defaults_pod/`

Summary:

- source commit: `cf3a479d7f40c36df1b3f44f68de20ef1b098221`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- seven-app canonical packet: `7 / 7` passed
- packet elapsed time: `442.002 s`
- claim-boundary violations: none
- dirty artifacts: none

## Triage Result

Triage artifact:

`docs/reports/goal2912_current_packet_scaled_defaults_triage_2026-05-31.json`

Result:

- status: `pass`
- performance targets: none
- top priority: none

Current app statuses:

| App | Status | Key evidence |
| --- | --- | --- |
| RayDB-style | `current_path_acceptable` | primitive-first fused grouped reduction remains selected |
| Triangle counting | `current_path_acceptable` | max query median `0.495 ms` |
| LibRTS spatial index | `tier_c_no_regression` | CPU/max-query ratio `1392.564x` |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity route only; row/overlay continuation remains explicit future work |
| RTNN | `current_path_acceptable` | CuPy/RTDL ratios: uniform `1.150x`, clustered `2.522x`, shell `7.640x` |
| Hausdorff/X-HD | `current_path_acceptable` | RTDL/CuPy ratio `0.940x` |
| RT-DBSCAN | `current_path_acceptable` | grouped-stream speedup vs prepared CuPy grid `4.166x` to `4.857x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | OptiX membership speedup `154.306x`; selected vector-sum partner `torch` |
| Contact manifold | `tier_c_no_regression` | not in seven-app packet |
| Robot collision | `tier_c_no_regression` | not in seven-app packet |

## Interpretation

This is the best current internal v2.5 performance posture:

- RT cores are easy to reach through the canonical app harnesses where RT traversal is the right primitive.
- Partner choice remains explicit: Torch is selected for Barnes-Hut vector sums, Triton remains visible but unpromoted, and CuPy remains a same-contract opponent/conformance baseline.
- The generic engine boundary remains intact; no app-specific native engine logic was added to clear the targets.
- The packet is honest about deferred work: RayJoin row/overlay continuation and Tier C apps are not turned into public speedup claims.

## Boundary

This is not release consensus and not a v2.5 release authorization.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, automatic Triton selection, package-install claims, or paper-reproduction claims.
