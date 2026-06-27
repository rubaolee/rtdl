# Review Debt: Goal4763 RT-BarnesHut Native ABI First Slice

Date: 2026-06-26

Debt status: open, allowed to proceed under the user's review-debt rule because this goal does not authorize release or performance claims.

## Review Request

Please critically review Goal4763:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/v4_rt_barneshut_native_route.py`
- `scripts/v4_rt_barneshut_native_feasibility_probe.py`
- `tests/v4_goal4762_rt_barneshut_native_feasibility_test.py`
- `tests/v4_goal4763_rt_barneshut_native_abi_first_slice_test.py`
- `future/v4/v4_goal4763_rt_barneshut_native_abi_first_slice_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4763_rt_barneshut_native_abi_first_slice_pod_2026-06-26.json`

## Verdict Needed

Use one of:

- `accept_goal4763_abi_first_slice_continue_goal4764`
- `accept_with_required_amendments`
- `reject_goal4763_overclaims_or_bad_abi`

## Questions For Reviewer

1. Is the native ABI shape (`prepare/run/destroy_rt_barneshut_author_3d`) a reasonable first slice for the author-semantics route?
2. Does the code correctly distinguish ABI symbol availability from native operator availability?
3. Is fail-closed `run` behavior acceptable until traversal/force implementation exists?
4. Does the POD dynamic export evidence prove the rebuilt library exposes the three symbols?
5. Are the claim boundaries strict enough to prevent ABI export from being misread as RT-BarnesHut reproduction?
6. Is Goal4764 correctly scoped as checksum-parity implementation before any scale/performance run?

## Non-Authorization

This review debt does not authorize:

- V4 release;
- native RT-BarnesHut operator claims;
- RT-BarnesHut paper reproduction claims;
- V2/V3/V4 same-semantics speed table;
- old 2D workflow divided by author binary;
- external author route counted as native V4.

It only records that Goal4763 is build/test-backed and awaiting external review.
