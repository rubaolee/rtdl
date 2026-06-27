# Review Debt: Goal4764 RT-BarnesHut Native ABI Checksum Route

Date: 2026-06-26

Debt status: open; implementation may continue under the user's review-debt allowance.

## Item

External 3-AI review is still required for Goal4764 completion.

Primary artifact:

- `future/v4/v4_goal4764_rt_barneshut_native_fallback_checksum_route_2026-06-26.md`

Evidence:

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4764_rt_barneshut_native_fallback_4096_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4764_rt_barneshut_native_fallback_8192_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4764_rt_barneshut_native_fallback_feasibility_pod_2026-06-26.json`

## Requested Review Questions

1. Does Goal4764 honestly represent a runnable native ABI checksum route rather than a native RT-core operator?
2. Are the 4,096 and 8,192 checksum gates sufficient to proceed to the RT-core replacement step?
3. Does the claim boundary correctly forbid speedup, paper-reproduction, V2/V3/V4 speed table, and generic V4 geomean claims?
4. Is `implementation_status_code=2` for `host_fallback_author_semantics_checksum_route` clear enough, or should the ABI expose a stronger enum/wording before Goal4765?
5. Is Goal4765 correctly framed as "replace fallback with author-compatible OptiX traversal/force behind the same ABI"?

## Non-Authorization

This review debt file does not authorize:

- V4 release based on RT-BarnesHut;
- RT-BarnesHut paper reproduction claims;
- speedup claims;
- public RT-core operator claims;
- V2/V3/V4 author-speed tables;
- generic operator geomean credit.

It only records that Goal4764 awaits external review while engineering continues.
