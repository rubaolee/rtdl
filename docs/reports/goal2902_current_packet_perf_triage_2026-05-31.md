# Goal2902: Current v2.5 Packet Performance Triage

Date: 2026-05-31
Status: accepted as internal performance-planning evidence

## Purpose

Goal2902 refreshes the current v2.5 benchmark-app packet on the RTX A5000 pod and converts the evidence into a 10-app performance triage. The purpose is to decide where v2.5 engineering should spend time next, without turning internal evidence into release wording.

This goal follows the current roadmap rule:

- make RT-core use easy from Python;
- keep partner choice explicit and user-controllable;
- compare RTDL plus partners against serious C++/CUDA/OptiX-style opponents;
- keep app-specific logic out of the native engine.

## Fresh Pod Packet

Artifact directory:

`docs/reports/goal2902_current_packet_perf_triage_pod/`

Summary:

- source commit: `f050d6d51533fed3e32acf19c4668c646236ad5f`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- seven-app canonical packet: `7 / 7` passed
- packet elapsed time: `416.581 s`
- claim-boundary violations: none

The packet is current-head evidence, not release authorization.

## Ten-App Triage

| App | Current route | Status | Key evidence | Next action |
| --- | --- | --- | --- | --- |
| `raydb_style` | primitive-first fused grouped reduction | current path acceptable | hit-stream plus Triton is `22.582x` to `205.085x` slower than primitive-first | keep primitive-first for exact fused reductions; reserve hit-stream partner paths for unfused continuations |
| `triangle_counting` | primitive-first OptiX summary | current path acceptable | max query median `0.441 ms` | keep primitive-first; add partners only for row-stream or compact-mask continuations |
| `librts_spatial_index` | prepared AABB index query | Tier C no-regression | CPU reference over max query ratio `1315.781x` | keep as RT-core prepared AABB no-regression baseline |
| `spatial_rayjoin` | prepared OptiX count/parity | current path acceptable, row/overlay deferred | max prepared query `0.209222 ms` | do not force Triton for count/parity; future work is row/overlay device continuation |
| `rtnn` | OptiX prepared ranked-summary aggregate | current path acceptable | CuPy over RTDL ratios `1.182x` to `2.480x` | keep current ranked-summary route green |
| `hausdorff_xhd` | RTDL/OptiX grouped adaptive nearest witness | performance target | RTDL `0.085914 s`, CuPy grid `0.004494 s`, RTDL/CuPy `19.119x` | highest priority: reduce adaptive RT threshold iterations or add fused tiled nearest-witness continuation |
| `rt_dbscan` | OptiX grouped stream plus CuPy components | current path acceptable | `3.820x` to `4.908x` over prepared CuPy grid | keep grouped stream; do not promote pure Triton components until same-contract win |
| `barnes_hut` | OptiX membership plus partner vector sum | performance target | OptiX membership up to `162.799x` over Embree; Triton vector sum `4.251x` slower than Torch | optimize segmented/block vector reduction or keep Torch/CuPy partner for this phase |
| `contact_manifold` | prepared bounded witness collection | Tier C no-regression | not in seven-app packet | measure no-regression unless exact refinement is partnerized |
| `robot_collision` | prepared any-hit pose flag | Tier C no-regression | not in seven-app packet | keep prepared RT any-hit no-regression track |

## Interpretation

The fresh packet is better than the older planning packet in one important way: RTNN is green at current head. The remaining measurable performance targets are now narrow:

1. Hausdorff/X-HD (`hausdorff_xhd`): exact RTDL/OptiX currently loses badly to the optimized CuPy grid baseline on the canonical input. This is the top v2.5 performance problem because it directly tests whether a learner can use RTDL for a serious RT-core-assisted nearest-witness application.
2. Barnes-Hut (`barnes_hut`): the RT membership phase is strong, but the Triton vector-sum continuation is not competitive with Torch on this shape. This should drive partner-selection honesty and/or a better generic segmented vector reduction.

The RayDB result is also important. It proves the opposite of a blanket "Triton everywhere" strategy: exact fused scalar grouped reductions should stay primitive-first. Partner continuations are for work the primitive cannot express efficiently.

## Boundary

This is not release consensus and not a v2.5 release packet.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, package-install claims, automatic Triton selection, or paper reproduction claims.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 scripts\goal2902_v2_5_current_packet_perf_triage.py \
  --packet-dir docs\reports\goal2902_current_packet_perf_triage_pod \
  --raydb-gate docs\reports\goal2896_pod_artifacts\goal2896_raydb_same_contract_performance_decision_gate_pod_69_30_85_171_2026-05-31.json \
  --output docs\reports\goal2902_current_packet_perf_triage_2026-05-31.json

[goal2902] status=pass apps=10 targets=2
```
