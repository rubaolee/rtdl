# RT-Core Evidence Matrix

Status: current v2.14 source-tree evidence guide.

Use this page when you want to know which benchmark apps currently demonstrate
RT-core value, which ones mostly test partner continuation, and which ones are
coverage or pressure-test evidence. This page is intentionally conservative:
it prevents the phrase "ten benchmark apps" from sounding like "ten broad
RT-core speedup claims." In short, the ten-app packet is not ten broad RT-core speedup claims.

## Reading Rule

A row is strong RT evidence only when the measured path is traversal-heavy,
prepared or repeated enough to amortize launch/setup cost, and compared against
a same-contract non-RT baseline. A passing benchmark front door is coverage
evidence, not automatically performance evidence.

## Current Matrix

| App | Current evidence class | What RTDL proves | What it does not prove |
| --- | --- | --- | --- |
| Hausdorff / X-HD | Mixed RT evidence | RTDL/OptiX threshold and active-frontier style paths exercise RT traversal for bounded distance decisions. | Exact Hausdorff, witness extraction, and whole-app speedup are not broad public claims. |
| Spatial RayJoin | Strong LSI RT evidence; mixed PIP evidence | LSI prepared scalar/count routes show prepared OptiX value. PIP is mixed: the refreshed human-scale public CDB slice is near parity and slightly Embree-faster, while Goal4368 shows the stricter full same-stream exact executor is faster on OptiX than Embree but still slower than RayJoin RT. | This is not a full RayJoin paper reproduction, not RTDL-beats-RayJoin wording, and not a single whole-app speedup claim. |
| RT-DBSCAN | Mixed RT + partner evidence | OptiX fixed-radius/grouped-stream primitives pair with explicit CuPy or Numba continuation. Goal4445 adds a compact component-signature output path that avoids per-point Python row materialization when the user only needs cluster-size/noise/core summaries. | RTDL does not claim arbitrary DBSCAN clustering acceleration, automatic partner optimization, or a DBSCAN-specific native engine ABI. Full per-point cluster rows remain the slower output contract. |
| Robot collision | Strong RT evidence | Prepared static-scene grouped-segment any-hit paths exercise repeated RT traversal with clean parity. Goal4428 records a 6.76x OptiX-over-Embree traversal row on the xlarge same-contract fixture, and Goal4446 removes the largest Python query-lowering debt without changing that contract. | The row is a sampled collision-screening contract, not a full robotics planning stack, continuous collision detector, exact solid collision route, or true-zero-copy claim. |
| Contact manifold | Mixed/coverage evidence | Bounded collect and witness primitives exercise generic RT row emission. | Rich manifold construction and downstream contact solving remain app logic. |
| RayDB-style | Strong primitive evidence | Fused generic grouped count/sum primitives can beat unfused partner continuation when the primitive exactly matches the query. | Arbitrary SQL/database acceleration is not claimed. |
| Barnes-Hut | Mixed explicit / fused partner beats prepared RT route | Prepared node-coverage threshold rows show an OptiX-over-Embree row-scoped win, Goal4438/4439 show RTDL/OptiX can emit aggregate-frontier device columns and feed Numba/CuPy partners, Goal4442 adds a fused CPU/Numba route, Goal4448 adds a Python-source Numba CUDA fused-subtree prototype that beats the current prepared RTDL/OptiX+Numba route on the measured scale ladder, and Goal4450 exposes that fused CUDA shape as the app front-door mode. | This is not Barnes-Hut RT-core speedup evidence. Use fused CPU/Numba or `fused_frontier_force_sum_bucketized_numba_cuda` for current no-C++ fused route evidence, and use prepared RTDL/OptiX+Numba only as RT device-column evidence unless a future fused RT-native/device primitive beats the fused baselines. |
| LibRTS spatial index | Strong RT evidence | Prepared AABB/spatial-index style query rows exercise RT traversal in a LibRTS-like contract. | It is not full mutable LibRTS and not a universal index replacement. |
| RTNN | Strong same-contract RTDL evidence / not paper reproduction | Goal4381 shows exact float64 RTDL/OptiX native ranked-summary aggregate is 10.14x faster than exact Embree on the 1M uniform row and 11.80x faster on the 262K shell row. Goal4443 shows the current RTNN app front door can run a 1M resident search scene with 65K query batches, CUDA graph replay, and same-stream CuPy/Numba reductions at about 5ms per batch with repeat=1000 second-level hot evidence. | It is not full RTNN paper reproduction, not official RTNN authors-code superiority, not arbitrary ANN-index acceleration, and exact float64 aggregate rows must not be mixed with float32 graph-bridge rows. |
| Triangle counting | Mixed primitive + partner-construction evidence | Generic graph relationship-count compositions and RT-Graph summary-contract paths pressure-test typed streams, reductions, and app-owned graph construction. Goal4444 removes the biggest unfairness in the Numba partner row by replacing M27's Python CPU-contract construction with direct binary vectorized summary construction before Numba device upload. | It does not prove broad triangle-counting acceleration for all graph families, RT-Graph paper-dataset superiority, or automatic CuPy-vs-Numba partner choice. |

## Performance Claim Checklist

Before using a benchmark row as performance evidence, make sure the artifact
names all of these:

- exact app row,
- exact backend,
- exact partner if one is used,
- exact hardware class,
- exact dataset or fixture scale,
- timing floor or repeat policy,
- same-contract baseline,
- claim-boundary flags.

If any item is missing, call the row compatibility or coverage evidence rather
than performance evidence.

## Current Positive Wording

Safe wording:

```text
Selected prepared, traversal-heavy RTDL/OptiX benchmark rows show strong
speedups over same-contract non-RT baselines in reviewed artifacts.
```

Blocked wording:

```text
RTDL accelerates all ten benchmark apps on RT cores.
```

## Related Evidence

- [Benchmark Evidence Index](benchmark_evidence_index.md)
- [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)
- [Goal4215 current scale-profile refresh](../reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md)
- [Goal4225 release-prep current scale packet](../reports/goal4225_release_prep_current_scale_packet_2026-06-09.md)
- [Goal4303 Fable5 review intake](../reports/goal4303_claude_fable5_review_intake_security_and_topk_actions_2026-06-11.md)
- [Goal4353 human-scale RT-core vs Embree CPU comparison](../reports/goal4353_human_scale_rt_vs_embree_run_20260612_pod_v3/summary.md)
- [Goal4354 RayJoin original-code same-stream comparison](../reports/goal4354_rayjoin_original_vs_rtdl_pod/goal4354_rayjoin_original_vs_rtdl_same_stream_summary.md)
- [Goal4358 v2.12 RTX A4000 RayJoin same-stream packet](../reports/goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13.md)
- [v2.12 release scoped RT-core vs Embree CPU comparison](../release_reports/v2_12/public_rt_vs_embree_comparison.md)
- [Goal4363 Robot Collision same-contract evidence](../reports/goal4363_rtx_a4000_v2_12_robot_collision_same_contract_2026-06-13.md)
- [Goal4446 Robot Collision NumPy lowering](../reports/goal4446_v3_0_m50_robot_numpy_lowering_2026-06-16.md)
- [Goal4364 RayDB-style same-contract evidence](../reports/goal4364_rtx_a4000_v2_12_raydb_same_contract_2026-06-13.md)
- [v2.13 release scoped RT-core vs Embree CPU comparison](../release_reports/v2_13/public_rt_vs_embree_comparison.md)
- [v2.14 release scoped RT-core vs Embree CPU comparison](../release_reports/v2_14/public_rt_vs_embree_comparison.md)
- [Goal4445 DBSCAN compact component signature](../reports/goal4445_v3_0_m49_dbscan_component_signature_2026-06-16.md)
- [Goal4450 Barnes-Hut fused Numba CUDA app front-door mode](../reports/goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_2026-06-16.md)
