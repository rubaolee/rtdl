# Goal5083 RT-BarnesHut Bounded Same-Input Closeout

Date: 2026-07-07

## Verdict Label

```text
completed_rt_barneshut_bounded_same_input_closeout__full_paper_not_closed
```

## Purpose

This goal closes the bounded same-input RT-BarnesHut line after Goals5063-5082.

The closeout is intentionally narrow. It records that RTDL now has a generic aggregate-hierarchy route capable of reproducing the patched-author same-prepared-state scalar force output on the bounded POD gate, while preserving the distinction between:

- bounded same-input reproduction,
- full paper reproduction,
- independent tree construction,
- narrow resident-kernel phase timing,
- whole-envelope performance.

## What Is Closed

### 1. Generic RTDL Aggregate-Hierarchy Route

The RTDL system now exposes a generic aggregate-hierarchy programming surface:

- `AggregateHierarchy3D`,
- `PreparedAggregateHierarchy3D`,
- `SizeDistanceOpening`,
- `LeafOnlyOpening`,
- `ContinuationPayloadOpening`,
- reducer constants such as `AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT`,
- CPU reference executor,
- optional Numba parity executor.

RT-BarnesHut-specific concerns remain in the paper app:

- patched-author binary orchestration,
- author prepared-state parsing,
- sentinel normalization,
- scalar force-output bridge,
- author force comparator,
- paper-specific manifest and gate runners.

### 2. Bounded Same-Input Correctness

Goal5079 live POD evidence passed the full gate.

Generic aggregate route against patched-author same-input prepared state:

```text
mismatch_count = 0
force_count = 32768
max_abs_error = 1830.0
max_rel_error = 2.1112736725325853e-06
opening.policy = continuation_payload_opening
```

Legacy author-optix-payload diagnostic route also matched:

```text
mismatch_count = 0
max_abs_error = 1139.0
max_rel_error = 2.6233255615631954e-06
```

This closes bounded same-input scalar force correctness for the prepared-state route.

### 3. Genericity Amendments

The strict review of Goals5079-5080 required proving that `ContinuationPayloadOpening` was not merely an RT-BarnesHut-shaped policy.

Goal5081 added an independent non-RT-BarnesHut synthetic consumer:

- synthetic hierarchy,
- `ContinuationPayloadOpening(max_ratio=0.5)`,
- `AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT`,
- no author prepared arrays,
- no sentinel adapter,
- no force law,
- no comparator.

Goal5082 hardened that proof by adding a fixture where accepted aggregate traversal must follow `rope_index` with `next_index != rope_index`.

External review verdicts:

```text
approve_goal5081_continuation_payload_genericity_amendment_and_non_rtbh_consumer
approve_goal5082_continuation_payload_rope_branch_hardening
```

### 4. Local Regression State

Latest local RT-BarnesHut / aggregate-hierarchy suite:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test tests.goal5081_continuation_payload_genericity_proof_test tests.goal5082_continuation_payload_rope_branch_test
Ran 76 tests in 30.944s
OK (skipped=1)
```

The local Python environment repeatedly prints:

```text
Could not find platform independent libraries <prefix>
```

This is a known local environment message and did not affect the test result.

## What Is Not Closed

### 1. Full Paper Reproduction

Not closed.

The current route uses patched-author prepared-state dumps. It does not independently reproduce the author's full input-generation, tree-construction, or complete end-to-end paper workflow.

Allowed wording:

```text
bounded same-input prepared-state reproduction
```

Forbidden wording:

```text
full RT-BarnesHut paper reproduction
independent author pipeline reproduction
full Section reproduction
```

### 2. Independent Tree Construction

Not closed.

The RTDL route consumes author prepared arrays. It does not yet prove that RTDL independently constructs an equivalent aggregate tree from raw particle input.

### 3. Whole-Envelope Performance

Not favorable to RTDL and not closed as a performance win.

Goal5079 / Goal5080 recorded the broader envelope:

```text
RTDL:
  extension_compile = 55.8721125125885 ms
  tree_prepare_cpu = 252.25137174129486 ms
  tensor_prepare_host_to_device = 160.36569327116013 ms
  resident_kernel_min = 0.856544017791748 ms
  total = 469.34572154283524 ms

Author:
  preprocessing = 18.804 ms
  execution = 166.642 ms
  total = 185.446 ms

Envelope ratio = 2.530902373428573
```

RTDL is about `2.53x` slower on this broader envelope.

### 4. Phase-Boundary Performance Acceptance

Not closed.

The narrow resident-kernel comparison is interesting but remains phase-boundary-limited:

```text
RTDL resident min = 0.856544017791748 ms
RTDL resident mean = 0.9283008098602294 ms
Author rt_core_force = 2.083 ms
ratio_min = 0.4112069216475026
ratio_mean = 0.4456556936438931
```

This may be discussed only with the whole-envelope caveat and only as a narrow phase result unless a separate phase-boundary acceptance goal approves it.

## Review Trail

Key review files:

- `history/internal_docs/review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`
- `history/internal_docs/review_goal5065_amendments_verified_signoff_2026-07-06.md`
- `history/internal_docs/antigravity_goals5063_5074_rt_barneshut_aggregate_hierarchy_consolidated_review_2026-07-06.md`
- `history/internal_docs/antigravity_goal5075_rt_barneshut_generic_aggregate_force_output_bridge_review_2026-07-06.md`
- `history/internal_docs/review_goals5079_5080_rt_barneshut_strict_phase_and_genericity_2026-07-07.md`
- `history/internal_docs/review_goal5081_continuation_payload_genericity_amendment_verified_2026-07-07.md`
- `history/internal_docs/review_goal5082_continuation_payload_rope_branch_hardening_verified_2026-07-07.md`
- `history/internal_docs/rt_barneshut_review_opinions_register_2026-07-06.md`

Known open review debt remains for earlier intermediate runner/package goals:

- Goal5076,
- Goal5078.

Goal5077 has an approved review. Goal5079 live POD evidence supersedes Goal5078 package-only evidence for final same-input correctness, but the review register intentionally keeps the intermediate debt visible instead of silently erasing it.

## Allowed Final Summary

```text
RTDL v2.14.x has a generic aggregate-hierarchy route for RT-BarnesHut-style hierarchical frontier reduction. On the bounded same-input prepared-state gate, the generic RTDL route matches patched-author scalar force output with zero mismatches. The route is not a full paper reproduction because RTDL consumes author prepared-state dumps and does not independently rebuild the author's full tree-construction pipeline. The broader reported envelope remains unfavorable to RTDL, while a narrow resident-kernel phase comparison remains phase-boundary-limited.
```

## Next Options

Recommended default:

```text
stop this bounded same-input line here
```

Optional future goals, only if explicitly authorized:

1. Phase-boundary acceptance goal for the narrow resident-kernel comparison.
2. Independent tree-construction goal from raw particle input.
3. Native/device aggregate-hierarchy backend goal using the CPU reference executor as oracle.
