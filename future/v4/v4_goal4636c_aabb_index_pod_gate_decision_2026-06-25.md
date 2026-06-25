# V4 Goal4636C AABB Index POD Gate Decision

Status: `goal4636c_aabb_index_pod_gate_passed_pending_frontdoor_catalog_not_release`

Decision: `accept_aabb_index_pod_gate_require_frontdoor_catalog_goal`

## What Was Tested

Goal4636C tested the generic AABB all-ops count surface as the third Goal4636
candidate after threshold-summary and grouped-any-hit both failed their
predeclared promotion gates.

- operator: `aabb_index_query_2d_all_ops_count`
- proposed API: `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- primitive: `AABB_INDEX_QUERY_2D`
- target row: `librts_spatial_index`
- scope: `rtdl_native_prepared_runner`
- fixture: 1,000,000 boxes x 1,000 queries
- operations: all (`point_contains`, `range_contains`, `range_intersects`)
- repeats: Embree 240, OptiX 240
- hardware: same RT-hardware POD, RTX A5000

Evidence:

- `future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json`
- `future/v4/reviews/goal4636c_aabb_index_target_protocol_review_record_2026-06-25.md`

## Result

| Gate | Floor | Result | Status |
| --- | ---: | ---: | --- |
| Cross-backend count parity | pass | pass | pass |
| Accepted contract family | pass | pass | pass |
| Embree / OptiX query median | >= 10.0x | 264.822x | pass |
| Embree / OptiX query total | >= 10.0x | 115.007x | pass |
| Public speedup claim authorization | false | false | pass |

Measured timings:

- Embree query median: `0.5198514759540558` sec
- OptiX query median: `0.001963019371032715` sec
- Embree query total: `130.3403503447771` sec
- OptiX query total: `1.1333229951560497` sec

## Interpretation

This is a real material V4 operator gate pass. It is not a whole-application
claim, not a LibRTS paper-reproduction claim, and not a release authorization.

The gate proves that the generic AABB all-ops count surface has strong
same-hardware evidence and should now move to a separate front-door/catalog
goal. The coverage table should not be promoted until that public V4 surface is
implemented and tested.

## Goal-Level Decision Audit

1. Was this a stupid goal-level decision?
   No. After two failed Goal4636 candidates, selecting AABB was justified
   because it targets a different generic relation/query class, requires no
   CuPy, and already had a serious all-ops prepared runner.

2. If not, what made it non-stupid?
   The protocol was predeclared, externally reviewed, amended before the POD
   run, run on a large fixture, and judged by frozen material floors.

3. Was there an alternative that avoided tunnel vision?
   Yes: stop Goal4636 entirely after two failures. The AABB gate was still worth
   running because it had a clear generic primitive and a credible strong
   same-contract hypothesis.

4. Can we switch path if the evidence demands it?
   Yes. The next path is not more candidate hunting; it is front-door/catalog
   productization for the passed AABB surface. If that productization fails,
   the result stays an internal gate pass and does not become public coverage.

## Next Required Goal

Start a front-door/catalog goal for
`v4_aabb_index_query_2d_all_ops_count_prepared_runner`:

- add the public V4 surface;
- add tests that route through that surface rather than directly through the
  old M30 script;
- refresh operator catalog and coverage audit;
- keep the claim boundary operator-level only;
- do not authorize V4 release or whole-app speedup wording from this gate alone.

## Non-Authorization

This decision does not authorize V4 release, release-candidate wording, broad
speedup claims, whole-app speedup claims, all-benchmark speedup claims, LibRTS
paper reproduction claims, authors-code comparison claims, public true-zero-copy
claims, Tier-3 callback support, raw OptiX callback support, CuPy performance
claims, C ABI, embedding, non-Python host claims, or app-specific native
kernels.
