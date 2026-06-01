# Goal2968: Current 10-App Performance Triage With RayDB Gate

Date: 2026-06-01
Status: triage passed with zero performance targets

## Purpose

Goal2959 made the seven-artifact current packet green. At that point RayDB was
listed in the triage as `not_indexed_in_current_packet` because the seven
canonical artifacts intentionally do not include the RayDB decision gate.

Goal2965 refreshed the RayDB same-contract decision gate on current main. Goal2968
therefore reruns the performance triage with the Goal2965 gate supplied via
`--raydb-gate`, so the triage now presents all 10 benchmark apps in one current
index.

## Artifact

- `docs/reports/goal2968_current_packet_plus_raydb_gate_triage_2026-06-01.json`

Inputs:

- packet dir: `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod`
- RayDB gate: `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`

## Result

| Field | Value |
| --- | --- |
| Status | `pass` |
| App rows | `10` |
| Performance targets | `0` |
| Top priority | `null` |
| Claim-boundary violations | `{}` |

RayDB is now indexed as a current gate row:

| App | Status | Route | Min hit-stream slowdown | Max hit-stream slowdown |
| --- | --- | --- | ---: | ---: |
| `raydb_style` | `pass` | `primitive_first_fused_grouped_reduction` | `30.138x` | `142.648x` |

## Boundary

This is a triage/indexing refresh, not new executable performance evidence. It
does not authorize release, public speedup wording, broad RT-core wording,
whole-app speedup wording, true zero-copy wording, package-install wording,
Triton preview auto-selection, paper reproduction, or app-specific native engine
customization.
