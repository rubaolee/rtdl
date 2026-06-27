# Review Debt: Goal4760 RT-BarnesHut Author-Contract Gate

Date: 2026-06-26

Status: review debt recorded; engineering may continue; no release authorization.

## Goal Under Review

Goal4760 implemented the RT-BarnesHut author-contract gate:

- `src/rtdsl/rt_barneshut_author_contract.py`
- `scripts/rt_barneshut_author_contract_probe.py`
- `tests/v4_goal4760_rt_barneshut_author_contract_test.py`
- `future/v4/v4_goal4760_rt_barneshut_author_contract_gate_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/rtdl_author_contract_4096.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/rtdl_author_contract_8192.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/rtdl_rt_barneshut_same_semantics_route_matrix_2026-06-26.json`

## Why This Debt Exists

The standing project rule requires 3-AI consensus for goal completion, or explicit recorded debt when reviewers are unavailable. This goal has local and POD tests, but it has not yet received Claude/Antigravity review.

## Requested External Review Questions

1. Does Goal4760 correctly distinguish a semantic author-contract gate from a V4 RT-core performance route?
2. Is the author-format loader faithful to the authors' treelogy and CSV parsing/scaling behavior?
3. Is the 3D z-order/bucket-tree/force CPU oracle close enough to serve as a same-semantics gate before a native RT-core route is implemented?
4. Are the non-authorization boundaries strong enough to prevent old 2D RTDL Barnes-Hut numbers from being divided against the authors' binary?
5. Is the route matrix honest in marking V2.14/V3.0.2 as `not_implemented_in_version` for the paper route?
6. Is Goal4761 correctly identified as the next required engineering step?

## Non-Authorization

This debt record does not authorize:

- V4 release;
- RT-BarnesHut paper reproduction wording;
- authors-code speedup wording;
- V2/V3/V4 author-binary performance comparison wording;
- treating the CPU oracle as an RT-core route.

It only records that Goal4760 engineering work is test-backed and awaiting external review.
