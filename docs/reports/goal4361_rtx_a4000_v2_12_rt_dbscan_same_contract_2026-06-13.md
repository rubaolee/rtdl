# Goal4361: RT-DBSCAN Same-Contract OptiX RT-Core vs Embree CPU Row

Date: 2026-06-13

Status: internal configured-route comparison; not public speedup authorization.

## Result Table

| Backend | Median Sec | Prepare Sec | Threshold Phase Sec | Numba Continuation Sec | Signature | RT-Core |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| OptiX | 0.315049268 | 1.337747950 | 0.119687332 | 0.159211490 | `True` | `True` |
| Embree | 17.313535127 | 0.360104169 | 16.608574028 | 0.180254284 | `True` | `False` |

Embree / OptiX median ratio: **54.96x**. Threshold-phase ratio: **138.77x**.

## Interpretation

This closes RT-DBSCAN as a contract-choice blocker for the internal optimized packet. Both rows use the same clustered3d 65,536-point input, same radius/min-neighbor policy, same Numba prepared-grid column-signature continuation, and produce the same component-size signature. The observed speedup is dominated by the threshold phase: OptiX RT-core count-threshold is about 139x faster than Embree threshold-capped rows here, while the Numba continuation is similar on both sides.

## Boundary

This is a same-contract RTDL+Numba configured-route row. It supports internal backend analysis for this route, not public whole-app or paper reproduction wording.
