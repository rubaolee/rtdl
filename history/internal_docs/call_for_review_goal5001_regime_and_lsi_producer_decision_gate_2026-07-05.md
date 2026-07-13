# Call For Review: Goal5001 Regime And LSI Producer Decision Gate

Please review:

```text
history/internal_docs/goal5001_regime_and_lsi_producer_decision_gate_2026-07-05.md
history/internal_docs/goal5001_regime_lsi_decision_artifacts_2026-07-05/fresh_one_shot_device_resident_carrier_top4.json
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

## Requested Verdict Label

```text
approve_goal5001_target_fresh_lsi_producer_first
```

or:

```text
revise_goal5001_decision_before_goal5002
```

## Review Questions

1. Does Goal5001 correctly classify `0.3295s` as prepared replay diagnostic, not
   fresh one-shot and not true query-many?

2. Does the fresh top4 POD artifact support the statement that the current
   fresh device-resident carrier route is approximately `4.816s`, with LSI
   producer approximately `2.588s`?

3. Is the LSI decomposition correctly interpreted?

```text
exact_pipeline_ensure + split_kernel_ensure ~= 0.913s
grouped_range_ensure + scaled_cache_ensure ~= 1.670s
native launch ~= 0.002s
```

4. Is it correct to reject true `query-many` claims for now because the current
   repeat/session CLI repeats the same left/right input and no distinct query
   batches have been measured?

5. Is the selected exit label correct?

```text
target_fresh_lsi_producer_first
```

6. Is the proposed next Goal5002 correct: first design/measure a generic fresh
   LSI compile/pipeline ensure reduction, rather than continuing downstream
   sort/carrier/consumer micro-optimization?

7. Does the plan preserve RTDL's generic-system boundary and avoid a hidden
   RayJoin-specific LSI producer optimization?

8. Should the CLI/help wording that calls same-input repeat mode
   `prepared/query-many` be treated as a required release-staging naming fix?

## Non-Authorization Boundary

This review should not approve:

- using `0.3295s` as a fresh or true query-many headline;
- continuing the old downstream-first Goals5001-5006 sequence;
- hiding the `~2.7s` LSI producer floor;
- adding RayJoin-specific LSI producer state to RTDL core;
- top4 author-performance ratios without a measured top4 author baseline.
