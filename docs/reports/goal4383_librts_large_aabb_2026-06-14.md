# Goal4383 LibRTS Large AABB P2

Date: 2026-06-14

## Verdict

P2 is implemented and measured. The LibRTS-style AABB row is no longer a tiny 1,024-box fixture only. It now has fresh same-contract RTDL OptiX-vs-Embree evidence at:

- 100,000 indexed boxes x 1,000 point/range queries;
- 1,000,000 indexed boxes x 1,000 point/range queries;
- paper-like uniform box/query widths of `0.005`;
- operation `all`: `point_contains`, `range_contains`, and `range_intersects`;
- prepared AABB index query contract on both sides.

This is still not exact LibRTS paper artifact reproduction, because the fixture is RTDL-generated uniform paper-like data, not the original paper dataset. It is now strong large-input evidence for the generic `AABB_INDEX_QUERY_2D` prepared-query contract.

## Correctness Fix

The first 1M Embree run returned `point_contains=6250`, while OptiX and historical authors-code evidence returned `6251`. A direct NumPy diagnosis showed:

- double exact envelope count: `6250`;
- float32 envelope count: `6251`;
- the single delta was a boundary/rounding case.

Because the native OptiX path and the authors LibRTS path use fp32 envelope traversal, the Embree native AABB predicate was aligned to the same fp32 envelope contract. The final Embree 1M row now matches OptiX and authors-code counts:

- `point_contains=6251`;
- `range_contains=693`;
- `range_intersects=25079`.

The fix is app-agnostic: it changes the generic Embree `AABB_INDEX_QUERY_2D` native predicate precision policy, not a LibRTS-specific branch.

## Performance Matrix

Timing basis: warm prepared-query median, repeat 5, warmup 1. Cold total includes scene prepare plus the hot query median. CPU reference counts are skipped for large rows to avoid O(n*m) validation; cross-backend counts match exactly in the final rows.

| Scale | Counts match | Embree cold total | OptiX cold total | Cold total speedup | Embree hot query | OptiX hot query | Hot-query speedup | Counts |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 100K boxes x 1K queries | yes | 0.7514s | 0.5422s | 1.39x | 8.5422ms | 0.2974ms | 28.72x | point 613, contains 66, intersects 2,477 |
| 1M boxes x 1K queries | yes | 6.6975s | 2.9561s | 2.27x | 21.0092ms | 1.5693ms | 13.39x | point 6,251, contains 693, intersects 25,079 |

## Explanation

The row is now reasonable and useful, but the wording must separate cold total from hot query.

The prepared hot-query phase is where RT cores matter most. At 1M x 1K, OptiX is 13.39x faster than Embree on the prepared query. At 100K x 1K, OptiX is 28.72x faster. These are strong RTDL primitive results for `AABB_INDEX_QUERY_2D`.

The cold total speedup is much smaller because scene construction dominates the one-shot total. At 1M, Embree spends 6.676s preparing the scene and only 21.0ms querying. OptiX spends 2.952s preparing and 1.57ms querying. Therefore the fair public sentence must say "prepared hot-query" when using the large hot speedup, and must report cold total separately.

## Evidence Files

- `docs/reports/goal4383_librts_large_aabb_2026-06-14/embree_100k_1k_paperlike_all_r5_fp32_contract.json`
- `docs/reports/goal4383_librts_large_aabb_2026-06-14/optix_100k_1k_paperlike_all_r5.json`
- `docs/reports/goal4383_librts_large_aabb_2026-06-14/embree_1m_1k_paperlike_all_r5_fp32_contract.json`
- `docs/reports/goal4383_librts_large_aabb_2026-06-14/optix_1m_1k_paperlike_all_r5.json`

## Public Wording

Allowed:

> On RTDL's generic prepared `AABB_INDEX_QUERY_2D` contract, paper-like uniform LibRTS-style fixtures show OptiX hot prepared-query speedups of 13.39x at 1M indexed boxes x 1K queries, with matching point/range counts against Embree. Cold total including scene prepare is 2.27x.

Not allowed:

> RTDL reproduces the full LibRTS paper.

Not allowed:

> The full LibRTS application is 13.39x faster.

The exact paper artifact and authors-code timing comparison remain separate follow-up work.
