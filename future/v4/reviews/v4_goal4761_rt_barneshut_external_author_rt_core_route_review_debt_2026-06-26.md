# Review Debt: Goal4761 RT-BarnesHut External Author RT-Core Route

Date: 2026-06-26

Status: review debt recorded; engineering may continue; no release authorization.

## Goal Under Review

Goal4761 implemented a V4-controlled wrapper for same-input RT-BarnesHut author RT-core execution:

- `src/rtdsl/v4_rt_barneshut_author_route.py`
- `scripts/v4_rt_barneshut_author_route_probe.py`
- `tests/v4_goal4761_rt_barneshut_author_route_test.py`
- `future/v4/v4_goal4761_rt_barneshut_external_author_rt_core_route_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_rt_barneshut_author_route_4096.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_rt_barneshut_author_route_8192.json`

## Requested External Review Questions

1. Is `external_author_rt_core_reference_route` the correct label for this route?
2. Does the route honestly distinguish RT-core execution from native V4 operator implementation?
3. Is checksum validation against the Goal4760 CPU oracle sufficient for this reference-route stage?
4. Are the claim boundaries strong enough to prevent V4 speed overclaiming?
5. Should Goal4762 pursue native V4 route implementation, or classify Barnes-Hut as reference-adapter-only for V4.0?

## Non-Authorization

This debt record does not authorize:

- V4 release;
- native V4 Barnes-Hut operator claims;
- V4-over-author speedup claims;
- V2/V3/V4 fair performance table claims;
- public RT-BarnesHut paper reproduction wording.

It only records that Goal4761 is implemented and awaits external review.
