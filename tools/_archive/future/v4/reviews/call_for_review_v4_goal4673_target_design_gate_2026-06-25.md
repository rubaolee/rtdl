# Call For Review: V4 Goal4673 Target Design Gate

Date: 2026-06-25

Status: review request; no POD or release authorization requested.

Please review:

```text
future/v4/v4_goal4673_target_design_gate_2026-06-25.md
future/v4/evidence/v4_goal4673_target_design_gate_2026-06-25.json
```

## Question

After the V2.14 primitive audit showed that every promoted benchmark app already
had a primitive or explicit partner route, Goal4673 selects
`AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` as the conditional Goal4674 target.

Do you accept this target-design decision?

## What To Check

1. Does the target honestly avoid counting V2.14 primitive/productization
   migration as a new V4 speed win?
2. Is `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` correctly classified as a
   V2.14-absent generic runtime lever, given the recorded `git show v2.14`
   evidence?
3. Is Barnes-Hut correctly limited to an app probe rather than engine identity?
4. Does the report correctly reject promotion of the old aggregate-tree fused
   weighted-vector implementation as-is?
5. Are the Goal4674 pre-POD gates strong enough: no host frontier rows in the
   hot handoff, frozen denominators, correctness parity, frozen numeric bars,
   and RT-core wording blocked unless OptiX trace is proven?
6. Should implementation continue only as local/static/protocol work until
   external review is available?

## Requested Verdict Labels

Use one:

- `accept_goal4673_target_design_continue_goal4674_static_gate`
- `accept_with_required_amendments`
- `reject_target_reselect_required`
- `reject_v4_high_performance_path_reframe_required`

## Non-Authorization

This review request does not authorize V4 release, public speedup wording,
whole-app high-performance wording, a POD run, RT-core speedup wording,
true-zero-copy wording, a Barnes-Hut engine kernel, C ABI, embedding, or
promotion of the old aggregate-tree fused weighted-vector route.

