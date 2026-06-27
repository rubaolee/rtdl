# Review Debt: Goal4762 RT-BarnesHut Native Feasibility Gate

Date: 2026-06-26

Debt status: open, allowed to proceed under the user's "review debt allowed" rule because this goal blocks overclaiming and does not authorize release.

## Review Request

Please critically review Goal4762:

- `src/rtdsl/v4_rt_barneshut_native_route.py`
- `scripts/v4_rt_barneshut_native_feasibility_probe.py`
- `tests/v4_goal4762_rt_barneshut_native_feasibility_test.py`
- `future/v4/v4_goal4762_rt_barneshut_native_feasibility_gate_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4762_rt_barneshut_native_feasibility_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4762_rt_barneshut_native_feasibility_pod_2026-06-26.json`

## Verdict Needed

Use one of:

- `accept_goal4762_fail_closed_gate_continue_goal4763`
- `accept_with_required_amendments`
- `reject_goal4762_gate_insufficient`

## Questions For Reviewer

1. Does Goal4762 correctly distinguish the existing 2D aggregate-tree fused route from the author RT-BarnesHut 3D route?
2. Are the required native symbols (`prepare/run/destroy_rt_barneshut_author_3d`) the right minimum ABI gate?
3. Is fail-closed behavior preferable to falling back to the old 2D route or external author binary?
4. Does the evidence sufficiently prove that the current V4 candidate lacks the native author route?
5. Are the claim boundaries strict enough to prevent another false Barnes-Hut speed/reproduction claim?
6. Is Goal4763 correctly identified as the next engineering step?

## Non-Authorization

This review debt does not authorize:

- V4 release;
- RT-BarnesHut paper reproduction claims;
- V2/V3/V4 same-semantics speed table;
- old 2D workflow divided by author binary;
- external author route counted as native V4.

It only records that Goal4762 engineering is test-backed and awaiting external review.
