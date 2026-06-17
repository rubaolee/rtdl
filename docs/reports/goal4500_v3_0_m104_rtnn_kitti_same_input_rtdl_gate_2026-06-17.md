# Goal4500 / V3 M104 RTNN KITTI Same-Input RTDL Gate

## Conclusion

M104 runs RTDL OptiX and Embree on the same bounded KITTI CSV. Count, nearest-id checksum, and distance-sum signatures match, but the tie-sensitive kth-id checksum differs; OptiX is 15.50x faster by median query time under this bounded gate.

The input is a bounded KITTI-family recipe, not an exact RTNN paper row. This packet only compares RTDL OptiX and RTDL Embree on the same CSV; author RTNN is the next gate.

## Input

- Export: `KITTI-1M` with 1,000,000 points at `/workspace/data/kitti/rtdl_goal4500/kitti_1m_points.csv`
- Radius: `1.0`
- K max: `50`
- Query/search contract: same CSV, ranked-summary aggregate, exact float64

## RTDL Matrix

| Backend | OK | Median Sec | Prepare Sec | Bounded Neighbors | Row Count |
|---|---:|---:|---:|---:|---:|
| OptiX | true | 7.802572 | 2.528946 | 49,248,495 | 1,000,000 |
| Embree | true | 120.927761 | 0.434335 | 49,248,495 | 1,000,000 |

## Boundary

- Same-input RTDL OptiX/Embree timing is valid only when both rows are `ok`; strict same-output wording additionally requires strict signature match.
- A tie-sensitive kth-id checksum mismatch must be reported separately from count/nearest/distance agreement.
- Author RTNN is not included in this packet.
- Paper-reproduction and public speedup wording remain blocked.

Artifacts:

- `docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.json`
