# Call For Review — Goal4909 Compiled Output Descriptor Plan

Date: 2026-07-03

## Review Target

Please review:

```text
history/internal_docs/goal4909_compiled_output_descriptor_plan_2026-07-03.md
```

Context:

- Goal4907 writer optimization succeeded.
- Goal4908 Python fast-path probe was byte-equal but slower and was reverted.
- Goal4909 proposes a real Numba/partner compiled descriptor gate before any
  further writer implementation.

## Requested Verdict Labels

Choose one:

```text
approve_goal4909_compiled_descriptor_implementation_gate
approve_with_required_amendments
block_goal4909_as_underdesigned_or_too_rayjoin_specific
```

## Questions

1. Is Goal4909 the correct next step after Goal4908 ruled out Python
   micro-fast-paths?
2. Is the plan materially different from Goal4908, i.e. a real compiled
   descriptor path rather than another Python branch reshuffle?
3. Is the `<1.50s` writer / `<3.60s` hot-body bar appropriate and falsifiable?
4. Does the plan keep the work in the app-layer/partner continuation boundary,
   rather than hiding RayJoin in RTDL core?
5. Should implementation be authorized as written?
6. If not, what exact amendment is required?

## Non-Authorization Reminder

Do not authorize:

- broad performance claims;
- full Section 5.7 performance claims;
- changing correctness/comparator boundaries;
- adding RayJoin-specific RTDL core/native code;
- treating this as RTDL primitive traversal acceleration.
