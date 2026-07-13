# Call For Review: Goal4954-A Binary Overlay Contract And Measurement Plan

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md`
- `history/internal_docs/goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md`
- `history/internal_docs/antigravity_review_goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md`

Requested verdict:

`approve_goal4954a_contract_measurement_plan_open_goal4954b`

or:

`block_goal4954a_until_amended`

## Context

Goal4954-A is the first subgoal opened by the approved Goal4954 program.

The owner invariant is mandatory:

> RTDL is a general spatial dataflow system. RayJoin is an app/stress test on
> top of RTDL.

Goal4954-A must therefore define a binary operator contract that can exist
outside RayJoin. RayJoin may adapt its paper-specific data into the contract,
but RTDL core cannot absorb RayJoin paper semantics.

## Review Questions

1. Does Goal4954-A define a binary overlay/event contract with generic names and
   generic semantics?

2. Does it keep RayJoin-specific items app-owned:
   - CDB loading;
   - AuthorOfficial comparison;
   - paper text writer;
   - output-chain byte equality;
   - app reconstruction from binary rows?

3. Does the ownership table correctly distinguish RTDL core progress from
   RayJoin app work?

4. Is `descriptor_pair_count` a reasonable first downstream consumer for
   proving binary operator value without parsing paper text?

5. Is the non-RayJoin proof requirement strong enough before any carrier or
   consumer is counted as RTDL-core progress?

6. Does the measurement plan preserve the distinction between:
   - paper-output correctness anchor;
   - writer-free binary operator performance benchmark?

7. Does it correctly require comparison against AuthorOfficial overlay compute,
   not author text dump?

8. Does it avoid pretending that removing the writer closes the compute gap?

9. Are the gates sufficient to prevent:
   - app-specific RayJoin core logic;
   - paper text semantics in RTDL core;
   - Layer 4 fusion work;
   - premature performance claims?

10. Should Goal4954-B open as measurement-only work with no columnar
    reprojection/sort implementation yet?

## Non-Authorization Boundary

Approval of Goal4954-A authorizes only Goal4954-B writer-free baseline
measurement.

It does not authorize:

- columnar reprojection/sort implementation;
- binary row construction implementation;
- public API exposure;
- native/core changes;
- Layer 4 fusion;
- raw callback support;
- app-specific RayJoin core work;
- performance claims before measurement.
