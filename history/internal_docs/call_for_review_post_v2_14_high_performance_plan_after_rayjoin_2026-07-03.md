# Call For Review: Post-v2.14 High-Performance Plan After RayJoin

Please review:

```text
history/internal_docs/post_v2_14_high_performance_plan_after_rayjoin_2026-07-03.md
history/internal_docs/rtdl_programming_model_direction_charter_2026-07-03.md
history/internal_docs/post_v2_14_architecture_direction_dataflow_fusion_compiler_2026-07-03.md
history/internal_docs/goal4888_core_phase_decomposition_gate_2026-07-03.md
history/internal_docs/claude_review_goal4887_fused_continuation_plan_2026-07-03.md
history/internal_docs/goal4886_authorpatch_vs_rtdl_performance_boundary_2026-07-03.md
```

## Requested Verdict

Preferred labels:

- `approve_plan_create_measurement_goal`
- `approve_with_required_amendments`
- `block_plan_as_premature_or_rayjoin_specific`

## Review Context

The v2.14 RayJoin paper-reproduction line is correctness-complete in a bounded
form, but the hot path is still much slower than the patched author
C++/CUDA/OptiX route.

Recent evidence:

```text
RTDL+Numba v2 one-shot end-to-end: 103.786 s
RTDL+Numba v2 query+output:         20.920 s
RTDL+Numba v2 core query compute:   18.880 s
AuthorPatch query+output:            0.844 s
AuthorPatch core query compute:      0.0421 s
```

Goal4887 proposed prepared/fused work but was blocked because it targeted
`3-8 s` without proving what part of the `18.880 s` core bucket is removable.

This plan accepts that critique and proposes:

```text
external review -> measurement gate -> branch by bottleneck -> only then implementation
```

## Questions

1. Does the plan correctly identify the root performance issue?
2. Does it correctly avoid treating callback absence as the whole explanation?
3. Does it properly preserve the data-flow compiler direction rather than
   turning RTDL into Python-wrapped OptiX?
4. Is Stage 1 measurement the correct immediate next step?
5. Are the branch conditions sufficient to prevent another V3-style
   implementation-before-source mistake?
6. Does the plan keep RayJoin as an exam rather than product-specific engine
   semantics?
7. Should the team create a formal measurement goal from this plan?

## Non-Authorization

This review must not be read as authorizing:

- implementation;
- public release wording;
- prepared sessions;
- row-buffer ABI;
- Numba partner API;
- native kernel changes;
- raw callback public API;
- RayJoin-specific shortcuts;
- hot-path performance claims.
