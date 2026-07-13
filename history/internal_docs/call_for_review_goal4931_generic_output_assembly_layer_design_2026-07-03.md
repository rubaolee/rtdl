# Call For Review: Goal4931 Generic Output-Assembly Layer Design

Date: 2026-07-03

Requested verdict labels:

- `approve_goal4931_design_authorize_goal4932_host_columnar_prototype`
- `approve_with_required_amendments`
- `block_goal4931_design`

## Files To Review

- `history/internal_docs/goal4931_generic_output_assembly_layer_design_2026-07-03.md`
- `history/internal_docs/goal4930_v2_14_2_layer0_writer_phase_decomposition_result_2026-07-03.md`
- `history/internal_docs/antigravity_goal4930_result_v2_14_2_layer0_writer_phase_decomposition_review_2026-07-03.md`
- `history/internal_docs/rtdl_next_version_performance_blueprint_layers_1_3_2026-07-03.md`

## Context

Goal4930 found that the remaining RayJoin Section 5.7 writer cost is dominated
by structural output-chain assembly, not final file/text write:

```text
structural assembly subtotal: ~2.001 s
bulk text/file write:         ~0.064 s
```

Goal4930 and its Antigravity review authorized only a design goal next. Goal4931
is that design goal. It must design a generic output-assembly layer without
putting RayJoin-specific output formatting into RTDL core.

## Questions For Reviewer

1. Does Goal4931 correctly follow Goal4930 by designing before implementation?
2. Is the proposed `GroupedSequenceAssemblyPlan` / `GroupedSequenceAssemblyResult`
   generic enough to be an RTDL feature rather than a RayJoin helper?
3. Does the design keep RayJoin exact text/topology formatting app-owned?
4. Are the app-specific red lines clear enough to prevent hiding RayJoin
   identity in RTDL core?
5. Is requiring a non-RayJoin proof workload before productization the right
   genericity gate?
6. Is the staged implementation path sensible: host-columnar prototype first,
   row-buffer compatible ABI second, device-resident implementation later?
7. Are the correctness gates sufficient, especially deterministic ordering and
   RayJoin byte equality through the app adapter?
8. Are the future performance targets bounded to the measured structural
   assembly layer, without overclaiming broad RTDL/RayJoin speedup?
9. Should the next goal be Goal4932, a host-columnar generic grouped-sequence
   assembly prototype, if this design is approved?

## Non-Authorization

This review must not authorize:

- broad performance claims;
- v2.14.2 release wording;
- RayJoin-specific output writer code in RTDL core;
- device-resident row-buffer implementation;
- native RTDL traversal changes;
- Layer 4 in-traversal fusion work.

It may only approve, amend, or block the design and the proposed next
host-columnar prototype goal.
