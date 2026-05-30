# Goal2732: Gemini Review Of Goal2727-2731 Primitive-First Correction

Date: 2026-05-30
Reviewer: Gemini 2.5 Flash
Status: recovered from Gemini CLI stdout after the CLI failed its own file-write call
Verdict: `accept-with-boundary`

## Independence Statement

This is an independent Gemini review distinct from Codex and Claude. Codex authoring is not independent review evidence, and Codex+Codex does not count as valid consensus.

The Gemini CLI produced the review analysis on stdout, but failed when it attempted to call its file-writing tool with an invalid parameter name. Codex recovered the review text into this file without changing the verdict.

## Scope

Gemini reviewed the v2.5 primitive-first correction after the RayDB evidence and triangle-counting plan update, including:

- `docs/reports/goal2727_raydb_prepared_grouped_reduction_opponent_2026-05-30.md`
- `docs/reports/goal2728_raydb_v2_5_primitive_first_planner_2026-05-30.md`
- `docs/reports/goal2730_triangle_counting_v2_5_primitive_first_plan_2026-05-30.md`
- `docs/reports/goal2731_raydb_minmaxavg_primitive_first_pod_evidence_2026-05-30.md`
- `docs/reviews/goal2729_claude_review_goal2726_2728_raydb_primitive_first_2026-05-30.md`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- the Goal2728, Goal2730, and Goal2731 tests.

## Findings

### 1. Primitive-First Rule

Gemini accepts the primitive-first rule: use an existing fused app-agnostic RTDL primitive when it exactly matches the computation, and reserve typed hit-stream or partner continuation for unfused continuations.

The reason is empirical and architectural. Goal2727 showed that RayDB-style count and sum are much faster through the prepared grouped-reduction primitive than through the prepared v2.5 typed hit-stream plus Triton path. Goal2731 extended that evidence to min, max, and avg-as-sum-count. Goal2730 applies the same rule to triangle counting by keeping scalar summaries on the fused native RTDL summary path rather than relabeling them as Triton benchmarks.

### 2. RayDB Min/Max/Avg Gap

Gemini accepts that Goal2731 closes the immediate measurement gap raised by Claude in Goal2729. The min, max, and avg-as-sum-count pod evidence demonstrates that the prepared fused RTDL primitive remains much faster than emitting typed hit-stream rows and reducing them through Triton for these matched reduction shapes.

### 3. Triangle Counting Claim Discipline

Gemini accepts the Goal2730 triangle-counting plan. The plan explicitly chooses `prepared_fused_generic_rt_summary` for scalar triangle counts and records the status as `primitive_first_plan_native_summary_not_relabelled_as_triton`. This avoids overclaiming and avoids presenting a native scalar summary as a Triton path.

### 4. Public Claim Boundaries

Gemini finds that public speedup, true-zero-copy, and paper-reproduction boundaries are preserved in the reviewed artifacts. Reports keep `public_speedup_claim_authorized` and `true_zero_copy_authorized` false, and the benchmark manifest continues to reject public-speedup or true-zero-copy authorization.

Goal2726 diagnostic ratios remain useful internal evidence, but they must not appear in public performance wording without clear asymmetric-baseline context.

### 5. Remaining Risks

Gemini identifies the following risks before broader v2.5 benchmark migration:

- Evidence is still primarily from one GPU class and one commit window.
- True zero-copy / same-pointer behavior still needs a formal claim-boundary review before any public zero-copy wording is authorized.
- Goal2726 diagnostic ratios must remain quarantined from learner-facing or public performance claims.
- Some source-inspection tests are brittle and should eventually be replaced or supplemented with runtime metadata assertions.

## Verdict

`accept-with-boundary`

The primitive-first correction is well-supported and should guide the v2.5 planner. The boundary is that broader hardware evidence, formal zero-copy review, and public-claims quarantine remain required before the policy is promoted as a public v2.5 performance claim.
