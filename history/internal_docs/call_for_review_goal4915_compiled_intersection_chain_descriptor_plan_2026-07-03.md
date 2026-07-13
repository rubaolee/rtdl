# Call For Review — Goal4915 Compiled Intersection-Chain Descriptor Plan

Date: 2026-07-03

Please review:

```text
history/internal_docs/goal4915_compiled_intersection_chain_descriptor_plan_2026-07-03.md
```

## Requested Verdict Labels

Choose one:

- `approve_goal4915_compiled_intersection_chain_descriptor_probe`
- `approve_with_required_amendments`
- `block_goal4915_as_more_writer_micro_tuning`
- `block_goal4915_as_too_rayjoin_specific_for_current_line`

## Review Questions

1. Does Goal4915 target the true remaining prepared-hot bottleneck after Goal4914?
2. Is the plan meaningfully different from the failed/shallow Goal4908 and marginal Goal4910 attempts?
3. Is the scope correctly app-layer only, with no RTDL core/native changes?
4. Are the acceptance bars (`writer <= 1.50s`, hot body `<= 3.60s`, byte equality) strict enough?
5. Is it correct to close as `correct_but_not_worth_productizing__python_text_writer_floor` if the bar is missed?
6. Should implementation be authorized?

## Non-Authorization Boundary

Approval must not authorize:

- changing RTDL core/native;
- changing public workspace/LSI/PIP semantics;
- hiding RayJoin logic inside RTDL;
- broad performance claims;
- raw OptiX callbacks;
- V3/V4 resurrection.
