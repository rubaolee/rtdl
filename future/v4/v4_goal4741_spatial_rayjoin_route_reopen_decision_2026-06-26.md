# V4 Goal4741 Spatial RayJoin Route Reopen Decision

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision:
`do_not_reopen_spatial_rayjoin_without_new_relation_topology_route`

## Purpose

Goal4728 closed `spatial_rayjoin` as a no-current-V4-route blocker. After
Goal4739/4740 updated the matrix and removed false Robot/RayDB distractions,
Spatial RayJoin is the next named blocker that could tempt another POD rerun.

Goal4741 checks whether there is a real reason to reopen it now.

## Decision

Do not reopen `spatial_rayjoin` for another POD run.

The current codebase has old RayJoin symbols and one measured generic
shape-pair subroute, but no complete current V4 app-level relation-topology
route. The measured subroute already failed the frozen speed-credit bars.

Running it again without a new route would be process churn.

## Evidence

Current route binding:

- `src/rtdsl/v4_app_route_binding.py::spatial_rayjoin`
- route class: `no_v4_app_route_blocker`
- full app route bound: `false`
- route actually uses V4 code: `false`
- dry run possible: `false`

Measured shape-pair subprobe:

- report: `future/v4/v4_goal4681_shape_pair_relation_pod_benchmark_2026-06-25.md`
- evidence: `future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/summary.json`

Frozen serious-result facts:

| Metric | Result |
|---|---:|
| correctness companion | pass |
| serious active-count parity | pass |
| V4 hot / V2.14 same primitive | 0.963x |
| V4 wall / V2.14 same primitive | 0.605x |
| V4 hot / V3.0.2 | 0.977x |
| speed-credit pass | false |

## Why This Is Not A V4 Performance Target Now

V2.14 already had prepared shape-pair active-count routes for the RayJoin
family. The only tested V4 relation operator is therefore a same-primitive
comparison, and it lost under the frozen bars.

The missing thing is not another repeat count. The missing thing is a complete
generic relation-topology V4 app route that covers a promoted RayJoin workload
class without silently falling back to V2/V3.

## Reopen Condition

`spatial_rayjoin` may be reopened only if all of these are written before POD:

1. A complete V4 app route, not only a shape-pair subprobe.
2. A frozen V2.14 denominator for the same workload class.
3. Correctness parity requirements.
4. Material-speed bars.
5. A proof that the route is generic relation/topology work, not a RayJoin
   app-identity native kernel.

Until those exist, this row remains:

`closed_no_current_v4_app_route_blocker`

## Next

Proceed to Goal4742:

Assemble the current post-repair matrix and release framing with:

- three app-level candidate rows;
- RayDB repaired as modest/no-regression;
- Robot boundary corrected but no V4 speed credit;
- Spatial RayJoin not reopened;
- custom predicate early-exit as a measured V4 eDSL/operator-pushdown workflow;
- final tag still requiring external review and wording discipline.

## Claim Boundary

Goal4741 authorizes no final V4 tag, no Spatial RayJoin speedup claim, no
RayJoin paper reproduction claim, no all-benchmark speedup claim, no app-specific
native kernel, and no hidden V2/V3 fallback.

## Goal-Level Decision Audit

1. Was I being foolish?

No. The foolish action would be rerunning the already-failed shape-pair subprobe
as if repetition could create a missing route.

2. If yes, what action made the decision foolish?

Not applicable.

3. Was there another path?

Yes. A real engineering path exists only if a complete relation-topology V4 app
route is designed before POD. That route does not currently exist.

4. Can I now try a different path that actually solves the problem?

Yes. Stop spending on Spatial RayJoin for now and converge the current V4
release framing honestly, while preserving the reopen condition for future
relation-topology work.

## Non-Authorization

Goal4741 authorizes no final V4 tag, no public speedup wording, no
Spatial-RayJoin speedup wording, no RayJoin paper reproduction wording, no
app-specific native kernel, and no true-zero-copy wording.
