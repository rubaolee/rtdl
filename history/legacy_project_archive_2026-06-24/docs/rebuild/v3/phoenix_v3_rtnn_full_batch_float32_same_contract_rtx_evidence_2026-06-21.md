# Phoenix V3 RTNN Full-Batch Float32 Same-Contract RTX Evidence

Status: `rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7`.

The 1,048,576-point repeat5 run is strong evidence that the prepared RTDL OptiX ranked_summary aggregate has a reusable hot-query advantage over a same-contract CuPy CUDA-core grid reference: 7.790x on the median hot query with matching integer signatures and a 1.21e-10 relative sum-distance error. It is not an end-to-end RTNN win. OptiX still loses cold-plus-query wall time at 0.393x and runner wall time at 0.627x because load, pack, and OptiX execution preparation dominate. This may be reviewed only as a prepared-hot-query candidate; wall/end-to-end wording remains blocked.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Hardware

- Host: `root@213.173.108.14 -p 11592`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- Compute capability: `8.9`
- RT hardware gate: `pass`
- OptiX library: `/root/rtdl_v3_rebuild_20260620/current/build/librtdl_optix.so`

## Main Row

- Evidence: `docs/rebuild/v3/evidence/rtnn_full_batch_float32_same_contract_1048576_r5_20260621`
- Points/repeat: `1048576` / `5`
- Same-contract signature match: `true`
- Sum-distance relative error: `1.207e-10`
- OptiX/CuPy hot-query speedup: `7.790x`
- OptiX/CuPy cold-plus-query speedup: `0.393x`
- OptiX/CuPy runner-wall speedup: `0.627x`

## Scale Rows

| Points | Repeat | Hot speedup | Cold+query speedup | Runner wall speedup | Parity |
| ---: | ---: | ---: | ---: | ---: | --- |
| 262144 | 3 | 2.467x | 0.171x | 0.278x | true |
| 1048576 | 3 | 8.099x | 0.395x | 0.597x | true |
| 1048576 | 5 | 7.790x | 0.393x | 0.627x | true |

## Not-M7 Blockers

- No external Claude/Gemini review has accepted the exact row.
- OptiX loses the cold-plus-query wall comparison to the same-contract CuPy grid reference.
- OptiX loses runner wall time to the same-contract CuPy grid reference.
- The RTDL route is float32 and exact=false, while the CuPy grid reference is exact.
- The row does not authorize RTNN whole-app, paper reproduction, V2 comparison, or universal NN claims.

## Next Engine Action

Keep RTNN ranked_summary open. The next valid engine work is to reduce or amortize OptiX pack/prepare overhead, add a stricter exact/tie-stable path, or seek external review for a narrowly worded prepared-hot-query row.

## Forbidden Shortcuts

- Do not call this RTNN M7 without external review and Codex consensus.
- Do not claim RTDL beats CuPy grid end-to-end or wall-clock on this row.
- Do not claim V3 solves nearest-neighbor workloads in general.
- Do not quote the 7.790x hot-query speedup without saying prepared-hot-query only.
- Do not reuse the old M106 787x-vs-Embree figure as public evidence.

## Goal-Level Decision Audit

Decision: Classify the fresh RTNN full-batch float32 same-contract RTX run as a prepared-hot-query candidate, not as an M7 or end-to-end win.

1. Was I foolish?
   No. The classification keeps the substantial hot-query improvement and the wall-time regression visible at the same time.
2. If yes, what actions made the decision foolish?
   The foolish action would be to market the 7.790x hot-query number while hiding the 0.393x cold-plus-query and 0.627x runner-wall regressions.
3. Was there another path that would have avoided getting stuck on that idea?
   Reject RTNN entirely because wall time loses, or promote it entirely because hot time wins. Either path would erase important evidence.
4. Can I now try a different path that actually solves the problem?
   Treat the row as a narrow candidate and direct engine work toward pack/prepare amortization or exact/tie-stable parity before promotion.
