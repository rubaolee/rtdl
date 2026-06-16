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
| RT-DBSCAN | Mixed RT + partner evidence | OptiX fixed-radius/grouped-stream primitives pair with explicit Numba continuation for component signatures. | RTDL does not claim arbitrary DBSCAN clustering acceleration or automatic partner optimization. |
| Robot collision | Strong RT evidence | Prepared static-scene collision count paths exercise repeated RT traversal with clean parity. | The row is a collision-screening contract, not a full robotics planning stack. |
| Contact manifold | Mixed/coverage evidence | Bounded collect and witness primitives exercise generic RT row emission. | Rich manifold construction and downstream contact solving remain app logic. |
| RayDB-style | Strong primitive evidence | Fused generic grouped count/sum primitives can beat unfused partner continuation when the primitive exactly matches the query. | Arbitrary SQL/database acceleration is not claimed. |
| Barnes-Hut | Scoped RT plus partner-route evidence | Prepared node-coverage threshold rows show an OptiX-over-Embree row-scoped win, Goal4438 shows the prepared aggregate-frontier device-column route can feed a faster Numba weighted-vector continuation than the same-contract CuPy continuation, Goal4439 exposes that route as a benchmark app mode, Goal4440 adds CPU/Embree host-materialized logical baselines, and Goal4441 optimizes their CPU vector continuation with Numba. | This is not Barnes-Hut force integration, a whole N-body speedup claim, or a pure RT-core speedup claim; Goal4438/4439 compare partners after the same RTDL/OptiX frontier contract, while Goal4440/4441 host baselines are diagnostic rather than public backend speedup evidence. |
| LibRTS spatial index | Strong RT evidence | Prepared AABB/spatial-index style query rows exercise RT traversal in a LibRTS-like contract. | It is not full mutable LibRTS and not a universal index replacement. |
| RTNN | Blocked RT-core claim / engineering evidence | Fresh prepared ranked-summary rows are near parity and useful for backend engineering. | v2.14 does not authorize RTNN as an RT-core neighbor-search speedup, full RTNN paper reproduction, or arbitrary ANN index performance. |
| Triangle counting | Mixed primitive/coverage evidence | Generic graph relationship-count compositions and candidate-row paths pressure-test typed streams and reductions. | It does not prove broad triangle-counting acceleration for all graph families. |

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
- [Goal4364 RayDB-style same-contract evidence](../reports/goal4364_rtx_a4000_v2_12_raydb_same_contract_2026-06-13.md)
- [v2.13 release scoped RT-core vs Embree CPU comparison](../release_reports/v2_13/public_rt_vs_embree_comparison.md)
- [v2.14 release scoped RT-core vs Embree CPU comparison](../release_reports/v2_14/public_rt_vs_embree_comparison.md)
