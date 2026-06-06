# Goal3602 v2.9 Benchmark Status After Resident Evidence

Date: 2026-06-06

## Purpose

Goal3602 refreshes the v2.9 benchmark interpretation after the post-closeout evidence added for RayJoin, Barnes-Hut, and LibRTS:

- Goal3595: clean long-repeat public-CDB RayJoin contract evidence;
- Goal3599: current-main Barnes-Hut resident-repeat evidence;
- Goal3601: clean v2.3/current same-contract LibRTS resident-repeat evidence.
- Goal3658: tuned RTDL/OptiX validated PIP device count evidence;
- Goal3660: reusable RTDL/OptiX PIP batch-executor throughput evidence.
- Goal3663: cross-slice PIP batch-executor confirmation on a 4096 public-CDB slice.

This document is a status refresh for internal engineering triage. It is not a release packet and does not authorize public speedup wording.

## Ten-Benchmark Status

| Benchmark app | Best current evidence | Reading |
| --- | --- | --- |
| `raydb_style` | Goal3565/3567: count `1.009085x`, sum `1.585627x` vs v2.3 | Repaired by generic small-group grouped-i64 sum/count fast path. This is the clearest v2.9 primitive win. |
| `contact_manifold` | Goal3567: `1.219528x` vs v2.3 | Positive packet row; no immediate v2.9 action. |
| `hausdorff_xhd` | Goal3567: `1.019555x` vs v2.3 | Positive packet row; exact-XHD work remains a future larger benchmark lane, not a v2.9 blocker. |
| `triangle_counting` | Goal3567: `1.029580x` vs v2.3 | Positive packet row; no immediate v2.9 action. |
| `rtnn` | Goal3562 targeted: `1.010948x`; Goal3567 packet row `1.061225x` | Treat as near-parity-positive with run variance, not a headline speedup. |
| `rt_dbscan` | Goal3563 seed probe: `1.012725x`; Goal3567 packet row `0.997206x` | Near parity; no clear source-change mandate in v2.9. |
| `robot_collision` | Goal3561 targeted: `1.001180x`; Goal3567 packet row `0.987619x` | Near parity; fresh clean v2.3 resident-repeat is not exposed without overlay-style measurement changes. |
| `librts_spatial_index` | Goal3601 clean same-contract resident pair: `1.005864x` | Clean parity row; not a performance blocker. |
| `barnes_hut` | Goal3599 current resident repeat: median `0.008080567s`, total measured hot query `11.637929s`; Goal3561 targeted ratio `0.997836x` | Current-main silent-partial issue closed. Do not publish a v2.9/v2.3 ratio until a truly comparable v2.3 resident baseline exists. |
| `spatial_rayjoin` | Goal3654/3658/3660/3663: LSI long-run `0.284x` vs RayJoin query timing, tuned one-shot/sequential PIP `0.283574ms`, batched PIP throughput `0.034225ms/request` on 512 and `0.051139ms/request` on 4096 | not one scalar app headline. Correct user story is contract-specific: RTDL/OptiX is strong for LSI, overlay active-count, and batched PIP throughput; one-shot/sequential PIP improved over CuPy but still trails RayJoin query timing. |

## RayJoin Contract Table

Goal3595 was the first clean current-RayJoin contract table because it used public CDB inputs, clean git status, repeat `200`, and matching counts:

| Contract | CuPy sec | RTDL/OptiX sec | RTDL/OptiX vs CuPy | Recommended route |
| --- | ---: | ---: | ---: | --- |
| PIP county512 scalar count | 0.000437917 | 0.002150856 | 0.2036x | CuPy dense CUDA-core route |
| LSI county512-soil512 count | 0.021059401 | 0.000185231 | 113.693x | RTDL/OptiX prepared route |
| Overlay county512-soil512 count | 0.049443172 | 0.000538940 | 91.742x | RTDL/OptiX prepared route |

The public-CDB three-contract geomean is `12.8536x` RTDL/OptiX-vs-CuPy, but this must not be converted into a single whole-app RayJoin claim because the correct route is mixed.

Goal3658 and Goal3660 supersede the old PIP routing conclusion:

| PIP contract | Best current RTDL route | Evidence | Reading |
| --- | --- | --- | --- |
| One-shot/sequential repeated positive assignment count | RTDL/OptiX prepared-points validated device count with `eps=1e-9` | Goal3658: exact `1417`, `0.283574ms`, `8.54s` total median over `30000` repeats | Faster than prior project-owned CuPy dense baseline, still slower than RayJoin `query_exec` reported query timing. |
| Batched repeated positive assignment count | RTDL/OptiX reusable prepared-point batch count executor with `eps=1e-9` | Goal3660: exact `1417`, `0.034225ms/request` on 512; Goal3663: exact `11331`, `0.051139ms/request` on 4096 | Strong RTDL throughput evidence across two public-CDB slices; explicitly not one-shot latency. |

## What Changed Since Goal3569

Goal3569 closed v2.9 internally with a composite packet and external consensus. After that, the user asked for stronger evidence around rows that looked weak or awkward. The new evidence changes the triage:

- RayJoin is no longer represented by one fragile `spatial_rayjoin_optix_prepared_full_route` row; it has contract-specific public-data tables for LSI, PIP one-shot/sequential, PIP batched throughput, and overlay active-count.
- Barnes-Hut is no longer a silent current-main partial row; it has more than 10 seconds of current resident hot-query evidence.
- LibRTS is no longer a stale near-parity row; it has a clean same-contract v2.3/current resident pair and is slightly positive.
- Robot collision remains near parity, but the clean v2.3 tree cannot expose the same resident-repeat API at the standard shape without a measurement overlay. Goal3561 remains the best current comparison evidence.

## Engineering Reading

The remaining v2.9 question is not "fix every 0.99x row." The meaningful reading is:

1. Primitive-first wins are real where the generic native primitive changed the amount of work or the reduction pattern, as in RayDB sum and RayJoin LSI/overlay.
2. Near-parity rows are often already limited by fixed contract cost, launch overhead, or measurement variance.
3. RayJoin PIP no longer belongs to CuPy for the measured project-owned routes: tuned RTDL/OptiX wins over prior CuPy for the bounded scalar-count row, and the reusable batch executor wins strongly for batched repeated requests on both 512 and 4096 public-CDB slices. The remaining gap is one-shot RTDL-vs-RayJoin latency and second-GPU confirmation.
4. Future performance work should target material semantic gaps and larger-scale contract stress, not sub-1% noise.

## Boundary

Goal3602 does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- paper reproduction claims;
- true zero-copy claims;
- automatic partner/backend selection;
- app-specific native-engine logic.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3602_v2_9_benchmark_status_after_resident_evidence_test
```
