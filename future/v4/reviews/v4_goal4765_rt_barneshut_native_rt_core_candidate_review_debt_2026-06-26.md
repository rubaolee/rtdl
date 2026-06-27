# Review Debt: Goal4765 RT-BarnesHut Native RT-Core Candidate

Date: 2026-06-26

Status: **open review debt**

Goal4765 has code changes, local tests, POD build evidence, POD unit tests, and
4096/8192 checksum evidence. It has **not** yet received the required external
3-AI completion audit. Per the project rule, this debt must be backfilled by
Claude/Antigravity or equivalent reviewers before it can be treated as fully
externally certified.

## Artifact Under Review

- `future/v4/v4_goal4765_rt_barneshut_native_rt_core_candidate_2026-06-26.md`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/v4_rt_barneshut_native_route.py`
- `scripts/v4_rt_barneshut_native_fallback_route_probe.py`
- `tests/v4_goal4765_rt_barneshut_native_rt_core_candidate_test.py`

## Evidence

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_4096_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_8192_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_fallback_regression_4096_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_warm_repeat_8192_pod_2026-06-26.json`

## Questions For Reviewer

1. Does Goal4765 honestly replace the Goal4764 host fallback force path with an
   OptiX RT-core traversal/force candidate behind the same ABI?
2. Are the 4096 and 8192 checksum gates sufficient for this goal's engineering
   completion, given that scale/performance gates are deferred to Goal4766?
3. Is the author DFS/rope metadata implementation close enough to the authors'
   `treeToDFSArray` and `installAutoRopes` flow for a candidate route?
4. Is the custom-primitive control geometry an acceptable candidate
   approximation of the authors' triangle control geometry, or must the next
   goal switch to literal triangle geometry before paper-reproduction review?
5. Are the claim boundaries strong enough to prevent this from being marketed
   as a public paper reproduction or speedup?
6. Is `input_columns_downloaded_for_tree_build=true` sufficiently explicit to
   prevent no-copy/device-residency overclaims?
7. Does the warm-run evidence correctly separate cold pipeline initialization
   from the warmed RT-force hot path?

## Requested Verdict Labels

Use one:

- `accept_goal4765_complete_pending_scale_and_release_review`
- `accept_with_required_amendments`
- `reject_requires_rework`
- `blocked_need_more_evidence`

## Non-Authorization

This review debt does not authorize:

- V4 release;
- public RT-BarnesHut paper-reproduction wording;
- V2.14/V3/V4 RT-BarnesHut speed tables;
- broad V4 high-performance claims;
- no-copy/device-residency claims for the tree build;
- treating Goal4765 as externally certified before review is backfilled.
