# Goal2959: Current Packet After RTNN Graph Chunking

Date: 2026-06-01
Status: pod packet passed; performance triage has zero targets

## Purpose

Goal2959 refreshes the current v2.5 canonical packet after Goal2958 added
graph-safe default query chunking to the RTNN graph replay harness.

The goal is to prove that the scale usability fix did not disturb the canonical
10-app packet and that the current packet still has zero performance targets in
the triage index.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `b4b8d7a6c6554b84870d9a5e67ffd16ebb8b76e8`

Artifacts:

- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2959_triage.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2797_triangle_counting.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2798_librts.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2799_spatial_rayjoin.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2800_rtnn.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2801_hausdorff_xhd.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2802_rt_dbscan.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2803_barnes_hut.json`

Packet summary:

| Field | Value |
| --- | --- |
| Status | `pass` |
| Artifacts | `7 / 7` |
| Source dirty | `[]` for all packet artifacts |
| Claim-boundary violations | `{}` |
| Elapsed | `427.193s` |
| Triage status | `pass` |
| Performance targets | `0` |

Key rows:

| App / row | RTDL | Opponent | Ratio |
| --- | ---: | ---: | ---: |
| RTNN uniform | `0.000121s` | `0.000138s` CuPy | `1.145x` CuPy/RTDL |
| RTNN clustered | `0.017264s` | `0.047068s` CuPy | `2.726x` CuPy/RTDL |
| RTNN shell | `0.000356s` | `0.002725s` CuPy | `7.652x` CuPy/RTDL |
| Hausdorff/X-HD | `0.007444s` | `0.008288s` CuPy | `0.898x` RTDL/CuPy |
| Barnes-Hut membership | OptiX | Embree | `158.977x` max |

## Boundary

This packet is internal engineering evidence. It does not authorize a v2.5
release, release tag action, public speedup wording, whole-app speedup wording,
broad RT-core wording, true zero-copy wording, package-install wording, Triton
preview auto-selection, or app-specific native engine logic.
