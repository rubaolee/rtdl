# Goal4378 Decision: Preserve v2.13, Use It As a Bridge, and Open v2.14

Date: 2026-06-14

Status: maintainer-direction decision record; not a release authorization.

## Decision

Preserve `v2.13` as the already-created source-tree release marker. Do not
rewrite it as if it was never public, and do not move any existing `v2.13` tag
without explicit maintainer action.

At the same time, treat `v2.13` as a corrective bridge after the RayJoin
Goal4376 findings. The next formal cleanup and benchmark-app performance
release will be `v2.14`.

Short form:

> v2.13 remains the row-scoped release marker we already produced. Goal4378
> freezes it with a post-publication caveat. v2.14 becomes the formal cleanup,
> benchmark-boost, and public-wording refresh release before V3.0.

## Why This Is the Safest Path

The repository already contains:

- `VERSION` set to `v2.13`;
- `docs/release_reports/v2_13/README.md`;
- `docs/release_reports/v2_13/publication.md`;
- `docs/release_reports/v2_13/tag_preparation.md`;
- v2.13 public wording and row-scoped comparison docs.

Therefore, silently relabeling v2.13 as purely internal would create version
history confusion. The safer governance action is:

1. preserve the v2.13 source-tree release record;
2. add a clear post-publication bridge addendum;
3. state that stronger benchmark-app cleanup and RayJoin author-hot-path
   interpretation are deferred to v2.14/V3.0 as appropriate.

## Corrected Interpretation After Goal4376

Goal4376 fixed the immediate RayJoin overlay Block x Water issue under the
RTDL route:

| Row | Author RT process wall | Goal4376 RTDL OptiX | RTDL Embree CPU | Correct readout |
| --- | ---: | ---: | ---: | --- |
| County x Zipcode | 5.614s | 5.767s | 9.954s | RTDL OptiX is near author process wall and faster than RTDL Embree CPU. |
| Block x Water | 28.088s | 28.471s | 34.905s | RTDL OptiX is near author process wall and faster than RTDL Embree CPU. |

But this is not author hot-compute parity. The author process wall includes
large map read/deserialization time, while RTDL spends much of its wall time in
runtime compute, preparation, materialization, and non-fused primitive/app
orchestration.

Allowed internal conclusion:

> RTDL OptiX can be near author process wall under the cached/preprocessed
> application-wall protocol, and it beats the RTDL Embree CPU route for the
> available Section 5.7 rows.

Blocked public conclusion:

> RTDL hot compute matches the RayJoin authors' specialized C++/CUDA/OptiX hot
> path.

## v2.13 Bridge Addendum Scope

The v2.13 bridge addendum does only this:

- freezes v2.13 as a row-scoped release marker;
- records that Goal4376 adds a stronger RayJoin overlay caveat;
- blocks author-hot-compute parity wording;
- points to v2.14 as the cleanup release;
- points to V3.0 for planner/device-resident/fused-execution work.

It does not:

- authorize a new release;
- move a tag;
- claim broad RT-core speedup;
- claim whole-application speedup;
- claim RTDL beats RayJoin;
- claim RayJoin paper reproduction;
- claim automatic partner selection;
- claim Intel/AMD GPU results;
- claim true zero-copy or full device residency.

## v2.14 Role

v2.14 is now the next formal release target. It should perform a full cleanup and
benchmark-app boost pass before V3.0.

"Boost" means every promoted benchmark app receives a current best-route audit,
same-contract comparison, explicit partner policy, phase explanation, and public
wording review. It does not mean every app must become an RT-core win.

v2.14 must have:

- current promoted benchmark-app inventory;
- best-known OptiX/RT-core route per row;
- best-known Embree CPU route per row when applicable;
- explicit partner choice and fixed-continuation policy;
- phase-level explanation for every speedup/slowdown;
- fresh current-head pod packet;
- public wording packet with zero unexplained rows;
- external review before publication.

## V3.0 Boundary

Author-level hot-path efficiency is a V3.0 target. V3.0 should not add
RayJoin-specific native engine code. It should add a generic planner,
device-resident streams, fused generic continuations, backend-specific lowering,
and profiler-grade phase accounting.

## Immediate Next Work

1. Add post-publication bridge notes to v2.13 release docs.
2. Create the draft v2.14 release folder and gates.
3. Ask external reviewers to audit this governance decision.
4. Start the v2.14 benchmark cleanup matrix only after the governance packet is
   visible.

