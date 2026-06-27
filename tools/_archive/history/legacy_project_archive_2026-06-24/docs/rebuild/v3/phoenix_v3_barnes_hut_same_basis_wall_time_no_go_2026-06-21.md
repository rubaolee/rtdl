# Phoenix V3 Barnes-Hut Same-Basis Wall-Time No-Go

Status: `barnes_hut_same_basis_no_go_current_frontier_shape_not_m7`.

This packet re-reads the M6 Barnes-Hut rerank artifact with one timing basis:
`repeat_seconds_median` wall time for every route. It does not authorize a release row.

```text
same_basis_timing_kind: wall_repeat_median_seconds
release_authorized: false
public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Same-Basis Result

| Bodies | Fastest wall route | Fastest wall | OptiX+Numba wall | OptiX+Numba / fastest | OptiX+CuPy / fastest | Contribution rows |
|---:|---|---:|---:|---:|---:|---:|
| 32,768 | `numba_cuda_fused` | 11.739 ms | 82.435 ms | 7.022x | 10.154x | 15,514,679 |
| 65,536 | `numba_cuda_fused` | 35.643 ms | 177.858 ms | 4.990x | 8.923x | 55,935,606 |
| 131,072 | `numba_cuda_fused` | 45.493 ms | 618.302 ms | 13.591x | 17.153x | 68,023,506 |

Same-basis wall timing removes the mixed-timing objection but does not rescue the current prepared RTDL/OptiX frontier-emission shape. The V3 performance path is the reusable fused aggregate-tree/vector partner route, not an app-specific Barnes-Hut native engine and not an RT-core speedup claim.

## Boundary

- Current prepared RTDL/OptiX frontier-emission rows remain not M7.
- The fused Numba CUDA route is not an RT-core result.
- This is not whole-app Barnes-Hut evidence, not paper reproduction, and not broad V3-over-V2 evidence.
- A future aggregate-frontier M7 attempt must be a separate reusable partner-contract review.

## Next Actions

- Keep current prepared OptiX frontier-emission Barnes-Hut rows out of M7.
- If aggregate_frontier is reopened, use a separate public-row review for the generic fused vector-accumulation partner contract.
- Do not claim RT-core acceleration for the Numba CUDA fused partner route.
- Do not use this packet as whole-app Barnes-Hut, paper reproduction, or broad V3-over-V2 evidence.
- Require external AI review before any M7 classification packet is updated from this evidence.

## Goal-Level Decision Self-Audit

1. Was I foolish? No. I rechecked the historical artifact under one wall-clock basis before deciding.
2. If yes, what actions made it foolish? The foolish action would be to keep blaming mixed timing after the wall-repeat fields already show the same ordering, or to promote a slow OptiX route because it contains RTDL machinery.
3. Was there another path? I could have rerun the pod first. That is still valid if external review asks for it, but the saved serious-run artifact already has the needed wall-repeat fields for this bounded decision.
4. Can I now try a different path? Advance V3 through the reusable fused aggregate/vector partner contract, with a separate M7 review, instead of forcing the current RT frontier-emission shape into release.

## Failures

- none
