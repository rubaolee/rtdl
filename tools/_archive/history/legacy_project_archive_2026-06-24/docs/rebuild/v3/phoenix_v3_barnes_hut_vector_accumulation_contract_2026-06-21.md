# Phoenix V3 Barnes-Hut Vector-Accumulation Contract

Status: `barnes_hut_vector_accumulation_contract_candidate_not_m7`.

This packet advances the `barnes_hut_vector_accumulation_frontier_shape`
queue item by turning it into a generic V3 engine-gap contract.
Apps are evidence harnesses only; this is not Barnes-Hut app development and not a new M7 row.

```text
release_authorized: false
public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## M6 Evidence Reading

- Status: `internal_m6_route_parity_evidence`
- Timing basis mixed: `true`
- Fastest route by scale:

  - `32768` bodies: `numba_cuda_fused`; prepared RTDL/OptiX+Numba over fastest `7.328x`; contribution rows `15514679`
  - `65536` bodies: `numba_cuda_fused`; prepared RTDL/OptiX+Numba over fastest `5.120x`; contribution rows `55935606`
  - `131072` bodies: `numba_cuda_fused`; prepared RTDL/OptiX+Numba over fastest `13.912x`; contribution rows `68023506`

M6 is serious route-parity evidence, but it is negative for the current prepared RTDL/OptiX frontier-emission shape: fused Numba CUDA is fastest at every rerun scale, and prepared RTDL/OptiX+Numba was slower than fused Numba CUDA by 5.120x to 13.912x on the 65,536 and 131,072 rows.

## Required Generic Contract

- Primitive: `AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE`
- Contract: `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`
- Status: `implemented_cuda_device_accumulation_not_rt_core`
- Executable today: `true`
- First backend target: `optix`
- CPU reference: `sum_aggregate_frontier_weighted_vectors_2d`
- Partner reference: `sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda`

Output columns:

- `source_id:int64[source_count]`
- `vector_x:float64[source_count]`
- `vector_y:float64[source_count]`
- `visited_count:uint64[source_count]`
- `aggregate_count:uint64[source_count]`
- `exact_count:uint64[source_count]`

Must avoid:

- aggregate-frontier row emission
- host frontier materialization
- host contribution materialization
- app-specific native engine callbacks
- automatic partner dispatch

RT-core claim requirements:

- OptiX implementation must launch an OptiX pipeline, not only CUDA kernels
- device program must call optixTrace or equivalent hardware traversal
- timing packet must separate BVH build, optixLaunch traversal, continuation, and copies
- CUDA-only fused implementation may be useful device evidence but not RT-core evidence

## V3 Engine Decision

Keep Barnes-Hut as a V3 engine-gap driver, not a release win. The current app-agnostic aggregate-tree fused weighted-vector primitive now accumulates directly into device vector/count columns instead of emitting aggregate-frontier rows before vector math, but the scorecard blocker is not release-cleared.

## Future M7 Requirements

- Improve the generic aggregate-tree fused weighted-vector primitive, not Barnes-Hut app-specific native code.
- Use the same source-id keyed vector summary as the CPU reference and Numba CUDA partner reference.
- Avoid aggregate-frontier row emission, host frontier materialization, and host contribution materialization on the hot path.
- Prove an OptiX pipeline launch with optixTrace or equivalent hardware traversal before any RT-core wording.
- Report BVH/build, optixLaunch traversal, continuation/vector accumulation, copy/materialization, and wall timing separately.
- Move the Barnes-Hut scorecard blocker to parity or better under the same contract.
- Require fresh RTX evidence, external review, and Codex consensus before reopening any M7 promotion.

## Forbidden Shortcuts

- Do not publish Barnes-Hut RT-core speedup wording from the current prepared frontier-emission route.
- Do not call fused Numba CUDA an RT-core result.
- Do not claim whole-app Barnes-Hut acceleration or paper reproduction.
- Do not use route parity as a public V3-over-V2 speedup claim.
- Do not add app-specific native Barnes-Hut engine callbacks to pass this gate.

## Review Status

- External review: `claude_cli_blocked_not_closed`
- 2-AI consensus: `not_closed_requires_external_review_before_m7`
- Call for review: `docs/reviews/call_for_review_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md`
- Blocked Claude attempt: `docs/reviews/claude_blocked_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md`

## Goal-Level Decision Audit

Decision: Turn Barnes-Hut/vector-accumulation into a generic V3 engine-gap contract, not an app win.

1. Was I foolish?
   No. The evidence says the current prepared RTDL/OptiX frontier-emission route is slower than fused Numba CUDA, so the honest V3 move is to define the missing reusable primitive.
2. If yes, what actions made the decision foolish?
   The foolish action would be to sell route parity, contribution-row scale, or OptiX participation as Barnes-Hut RT-core acceleration while the fastest measured route is not RTDL/OptiX.
3. Was there another path that would have avoided getting stuck on that idea?
   Tune Barnes-Hut-specific code or keep quoting old M101/M121 reports. That might improve a demo, but it would not establish a language-level V3 capability.
4. Can I now try a different path that actually solves the problem?
   Use this packet to drive a generic fused vector-accumulation implementation and keep all M7, release, RT-core, and broad V3-over-V2 claims blocked until the primitive has fresh evidence.
