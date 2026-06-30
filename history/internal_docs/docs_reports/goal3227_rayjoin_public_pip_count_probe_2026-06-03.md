# Goal3227: RayJoin Public PIP Count Probe

Date: 2026-06-03

## Purpose

Goal3227 adds the public CDB PIP sibling to the Goal3218 public LSI probe and
Goal3225 public overlay active-count probe.

It reuses Goal2159 public CDB slice materialization and checks that the prepared
OptiX point/closed-shape count route matches the CPU reference
`positive_assignment_count` contract on the bounded `pip_county512` case.

## Artifact

- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.json`
- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.stdout`

Pod metadata:

- Commit: `92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3`
- GPU: `NVIDIA A40, 570.211.01`
- CUDA driver query: present
- nvcc version: present
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Warmups: `1`
- Repeats: `5`
- Status: `pass`

| Case | Public Slice | Expected Positive Assignments | Observed Counts | Median Prepared Count (s) |
| --- | --- | ---: | --- | ---: |
| `pip_county512` | county 0:512 | 1430 | `[1430, 1430, 1430, 1430, 1430]` | 0.06793256662786007 |

## Interpretation

Goal3227 confirms the current prepared OptiX PIP count route on a bounded public
Brazil county CDB slice. Together with Goal3218 and Goal3225, this gives public
count/parity coverage for all three current RayJoin count-family workloads:

- PIP: public positive-assignment count,
- LSI: public segment-intersection count via fused dense left-id count,
- overlay_seed: public active pair-dependency count.

The native engine remains app-agnostic. It sees the generic
`POINT_CLOSED_SHAPE_MEMBERSHIP_2D` prepared count contract; RayJoin
interpretation remains in Python.

The refreshed `92e16b86` pod artifact also normalizes the claim-boundary
schema at every artifact level: top-level, per-row, and per-measurement blocks
all use the same six canonical false claim flags.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The full RayJoin paper-scale comparison remains open.
