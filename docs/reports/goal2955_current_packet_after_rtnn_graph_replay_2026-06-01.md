# Goal2955: Current Packet After RTNN Graph Replay

Date: 2026-06-01
Status: pod packet passed; performance triage has zero targets

## Purpose

Goal2955 refreshes the current v2.5 canonical packet after Goal2952 moved
Hausdorff to the target-8192 default and Goal2954 moved RTNN to the prepared
query CUDA graph replay route.

This packet answers the immediate engineering question: after those two route
tuning fixes, does the current 10-app v2.5 benchmark foundation still have a
known performance target in the triage index?

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `747716c7141341b43a4bed37f66c53d0ff2bcc14`

Artifacts:

- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2855_summary.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2955_triage.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2797_triangle_counting.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2798_librts.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2799_spatial_rayjoin.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2800_rtnn.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2801_hausdorff_xhd.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2802_rt_dbscan.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2803_barnes_hut.json`

Packet summary:

| Field | Value |
| --- | --- |
| Status | `pass` |
| Artifacts | `7 / 7` |
| Source dirty | `[]` for all packet artifacts |
| Claim-boundary violations | `{}` |
| Elapsed | `459.078s` |
| Triage status | `pass` |
| Performance targets | `0` |

## Key Rows

RTNN now uses `ranked-summary-aggregate-prepared-query-batch-graph-float32`.
All three canonical distributions are faster than the same-contract CuPy grid
opponent in the current packet:

| Distribution | RTDL sec | CuPy sec | CuPy/RTDL ratio |
| --- | ---: | ---: | ---: |
| uniform | `0.000122` | `0.000139` | `1.147x` |
| clustered | `0.017265` | `0.046990` | `2.722x` |
| shell | `0.000363` | `0.002726` | `7.503x` |

Hausdorff remains exact and no longer appears as a performance target:

| App | RTDL sec | CuPy sec | RTDL/CuPy ratio |
| --- | ---: | ---: | ---: |
| Hausdorff/X-HD | `0.007488` | `0.008310` | `0.901x` |

Barnes-Hut remains healthy under measured partner selection:

| Row | Result |
| --- | --- |
| Max OptiX membership speedup vs Embree | `163.930x` |
| Selected vector-sum partner | `cupy` |
| Selected vector-sum median sec | `0.000776` |

## Interpretation

This is the first current v2.5 packet where the triage script reports zero
performance targets across the 10-app foundation. The important design pattern
is the same in both recent fixes:

- choose an existing generic RTDL route before adding primitives;
- prefer primitive-first fused reductions where the primitive already expresses
  the computation;
- use prepared query CUDA graph replay for repeated fixed-radius ranked-summary
  workloads;
- keep partner selection measured and explicit rather than automatic.

## Boundary

This packet is internal engineering evidence. It does not authorize a v2.5
release, release tag action, public speedup wording, whole-app speedup wording,
broad RT-core wording, true zero-copy wording, package-install wording, Triton
preview auto-selection, or app-specific native engine logic.
