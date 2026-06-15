# RTDL v2.14 Benchmark-App Boost Gates

Status: draft gate checklist.

## Meaning Of "Boost"

For v2.14, "boost all benchmark apps" means disciplined optimization and
evidence refresh across all promoted benchmark apps. It does not mean forcing
every benchmark app to show an RT-core win.

Each row must land in one of three honest buckets:

| Bucket | Meaning |
| --- | --- |
| RT-core win | OptiX/RT-core is faster than the same-contract Embree CPU route under the documented protocol. |
| CPU/partner win | Embree CPU or a fixed partner route is faster; publish as such or keep internal. |
| Blocked | The row lacks same-contract evidence, current best route, phase explanation, or reviewer acceptance. |

## Gate 1: Inventory

- Current promoted benchmark-app list is frozen for the v2.14 packet.
- Demoted learner, tutorial, research, or exploratory apps are not counted as
  promoted benchmark apps.
- Each promoted app has exactly one release-row owner or an explicit reason for
  multiple rows.

## Gate 2: Same-Contract Comparison

For each comparison row:

- input data and scale are identical;
- output contract is identical or explicitly caveated;
- repeat/warmup protocol is identical or explicitly caveated;
- partner continuation is fixed or separately measured;
- CPU thread policy and GPU device policy are documented.

## Gate 3: Best-Known Route

For each backend:

- use the best known current RTDL route;
- avoid stale unoptimized artifacts;
- document any known optimization debt;
- explain why remaining debt does or does not block public wording.

## Gate 4: Phase Explanation

Each speedup or slowdown must have a phase-level explanation. The explanation
must point to measured or instrumented phases such as:

- traversal;
- build/prepare;
- upload/download;
- row materialization;
- partner continuation;
- Python/native wrapper overhead;
- output assembly;
- CPU threading.

Rows with unexplained speedups or slowdowns are blocked from public wording.

## Gate 5: Data Movement And Materialization

Each row must record whether the path:

- uploads large inputs per repeat;
- downloads rows or summaries per repeat;
- materializes large host arrays;
- keeps device-resident columns;
- uses compact outputs or summaries;
- pays avoidable app/Python reconstruction.

Avoidable movement should be fixed before release or listed as blocking debt.

## Gate 6: Native Boundary

Native RTDL must remain app-agnostic.

Allowed native concepts:

- segment-pair intersection;
- directed segment point-location;
- closed-shape membership;
- AABB index query;
- fixed-radius search;
- first-hit / nearest-hit rows;
- compact positive streams;
- grouped reductions;
- device columns.

Blocked native concepts:

- RayJoin-specific map semantics;
- DBSCAN-specific clustering policy;
- Barnes-Hut-specific force law;
- benchmark-app-specific ABI names;
- hidden route selection that changes app semantics.

## Gate 7: RayJoin Author-Code Caveat

RayJoin rows must separate:

1. author process wall;
2. author hot-processing phases;
3. RTDL OptiX app/runtime wall;
4. RTDL exposed traversal/launch time;
5. RTDL OptiX-vs-Embree same-route comparison.

Do not use near author process wall as evidence of author-hot-compute parity.

## Gate 8: Public Wording

Every public sentence must name:

- app;
- row;
- contract;
- backend pair;
- partner policy;
- hardware;
- timing protocol;
- speedup direction;
- caveat.

No broad or whole-app wording is allowed unless a separate release gate proves
it and reviewers explicitly accept it.

## Gate 9: Review

v2.14 requires external review before publication. Reviewers should reject the
packet if any row:

- compares stale artifacts;
- hides partner differences;
- lacks phase explanation;
- presents a process-wall comparison as hot-compute parity;
- implies all benchmark apps are RT-core wins;
- weakens app-agnostic native-engine boundaries.

