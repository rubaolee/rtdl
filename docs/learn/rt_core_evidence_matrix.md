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
| Spatial RayJoin | Strong LSI RT evidence; mixed PIP evidence | LSI prepared scalar/count routes show prepared OptiX value. PIP is mixed: the refreshed human-scale public CDB slice is near parity and slightly Embree-faster, while stricter prepared-executor rows are faster on OptiX than Embree and still slower than RayJoin RT. | This is not a full RayJoin paper reproduction, not RTDL-beats-RayJoin wording, and not a single whole-app speedup claim. |
| RT-DBSCAN | Mixed RT + partner evidence | OptiX fixed-radius/grouped-stream primitives pair with explicit Numba continuation for component signatures. | RTDL does not claim arbitrary DBSCAN clustering acceleration or automatic partner optimization. |
| Robot collision | Strong RT evidence | Prepared static-scene collision count paths exercise repeated RT traversal with clean parity. | The row is a collision-screening contract, not a full robotics planning stack. |
| Contact manifold | Mixed/coverage evidence | Bounded collect and witness primitives exercise generic RT row emission. | Rich manifold construction and downstream contact solving remain app logic. |
| RayDB-style | Strong primitive evidence | Fused generic grouped count/sum primitives can beat unfused partner continuation when the primitive exactly matches the query. | Arbitrary SQL/database acceleration is not claimed. |
| Barnes-Hut | Scoped RT evidence | Prepared node-coverage threshold rows show an OptiX-over-Embree row-scoped win. | This is not Barnes-Hut force integration or a whole N-body speedup claim. |
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
- [v2.12 release scoped RT-core vs Embree CPU comparison](../../history/release_reports/v2_12/public_rt_vs_embree_comparison.md)
- [v2.13 release scoped RT-core vs Embree CPU comparison](../../history/release_reports/v2_13/public_rt_vs_embree_comparison.md)
- [v2.14 release scoped RT-core vs Embree CPU comparison](../release_reports/v2_14/public_rt_vs_embree_comparison.md)
