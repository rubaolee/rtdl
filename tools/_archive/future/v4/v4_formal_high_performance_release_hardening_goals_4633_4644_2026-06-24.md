# V4 Formal High-Performance Release-Hardening Goals

Date: 2026-06-24

Status: `pending_owner_review_do_not_execute`

Current valid label before these goals finish:

- `development_state_performance_preview_not_release`

Target:

- formal high-performance V4 release, only if the gates below pass.

This file turns the required route into a concrete goal list:

1. clear review debt;
2. expand measured operator coverage;
3. handle the weighted-sum candidate;
4. run serious all-app / promoted benchmark release gates;
5. make user docs/examples clean and current;
6. obtain 3-AI final release authorization;
7. publish only after authorization.

## Numbering Note

Goal4633 was already opened as the weighted-sum promotion-gate protocol:

- `future/v4/v4_goal4633_weighted_sum_promotion_gate_protocol_2026-06-24.md`

To avoid rewriting history or silently renumbering live artifacts, this roadmap
keeps Goal4633 as the weighted-sum gate. Review-debt cleanup is treated as the
current baseline/precondition because Antigravity has already reviewed and
closed the 9 substantive Goal4626-4632 scorecard review debts:

- `future/v4/reviews/v4_remaining_debt_after_antigravity_scorecard_review_and_forward_message_2026-06-24.md`

If the owner rejects this numbering, renumber before executing any goal.

## P0. Review-Debt Baseline

Status: `done_pending_owner_acceptance`

Purpose:

- ensure no historical/procedural review debt is being mistaken for current
  engineering release debt.

Current evidence:

- Antigravity closed the 9 Goal4626-4632 scorecard review-debt items.
- Older procedural debts were classified as closed or superseded.
- Remaining blockers are engineering/release blockers only.

Exit gate:

- owner accepts the remaining-debt tracker as the baseline;
- no old blocked review file may block engineering work unless a reviewer
  explicitly reopens it.

No POD required.

## Goal4633. Weighted-Sum Promotion Or Rejection Gate

Purpose:

- resolve `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`;
- move it from candidate to measured Torch CUDA Tier-2 surface, keep it
  candidate, or reject it for V4.0.

Why this matters:

- `triangle_counting` remains candidate-bound through weighted-sum;
- existing candidate evidence is positive but too narrow:
  - 32768 rays/triangles: `2.047x`, parity passed;
  - 131072 rays/triangles: `1.557x`, parity passed;
  - only 5 candidate-level repeats.

Tasks:

- apply Claude's required wording amendment:
  - rename "same-contract comparison" to "same-operator comparable-route
    comparison";
  - state that the ratio measures host-materialization path cost versus
    device-resident output path cost, not pure kernel-vs-kernel speedup.
- run the predeclared POD gate:
  - shapes: `32768`, `131072`, `262144`, `524288`;
  - warmups: `5`;
  - repeats: `30`;
  - Torch CUDA only;
  - parity at every shape;
  - device output and no hot-path host scalar materialization metadata.
- record one decision:
  - `promote_weighted_sum_measured_torch_v4_tier2`;
  - `keep_weighted_sum_candidate_not_promoted`;
  - `reject_weighted_sum_for_v4_0`.

Exit gate:

- all shapes complete or the failure is explicitly classified;
- parity result recorded;
- per-shape ratios and geomean recorded;
- if promoted, tests/catalog/docs updated so measured/candidate status cannot
  drift;
- if not promoted, triangle-counting remains candidate or excluded.

Estimated time:

- 2-4 hours with POD available.

Review:

- Claude already returned `approve_with_required_amendments`.
- Antigravity review may be debt if CLI returns empty output.
- Goal completion requires 3-AI audit or recorded debt according to owner rule.

## Goal4634. Coverage Audit Refresh After Weighted-Sum Decision

Purpose:

- update the 10 promoted benchmark-family coverage split after Goal4633.

Tasks:

- update `src/rtdsl/v4_coverage_audit.py`;
- update tests for coverage status counts;
- distinguish:
  - strong measured;
  - partial measured;
  - candidate;
  - deferred.
- identify the next two coverage blockers that can be addressed by generic
  operators, not app-specific kernels.

Exit gate:

- coverage split is current;
- every remaining partial/candidate/deferred row has a next action;
- no broad speedup wording is authorized.

Estimated time:

- 1-2 hours, no POD unless validation needs GPU smoke.

## Goal4635. Expand Measured Operator Coverage: First Generic Coverage Blocker

Purpose:

- add or reject one new measured generic Tier-2 operator that moves a current
  partial/candidate/deferred coverage row.

Allowed operator classes:

- generic continuation or push-down operators only;
- examples: component union, ranked/top-k summary, AABB/relation prefilter,
  grouped reduction variants.

Forbidden:

- app-identity kernels such as DBSCAN, Barnes-Hut, RayJoin, triangle-counting,
  or librts-specific kernels.

Tasks:

- predeclare the chosen blocker and operator hypothesis;
- implement or expose the generic operator surface;
- run parity and POD performance gate;
- update catalog and coverage audit only if the gate passes.

Exit gate:

- one named coverage row moves measurably, or the candidate is rejected with
  evidence;
- the gain source is runtime/operator-level, not app-specific code.

Estimated time:

- 4-10 hours depending on chosen operator.

## Goal4636. Expand Measured Operator Coverage: Second Generic Coverage Blocker

Purpose:

- prove Goal4635 was not a one-off by moving a second coverage blocker with the
  same V4 generic-operator rules.

Tasks:

- select a second blocker with a different continuation class when possible;
- repeat the same predeclared parity/performance gate;
- update catalog/coverage/tests.

Exit gate:

- second named coverage row moves or is rejected with evidence;
- measured operator coverage improves beyond the Goal4627 split;
- no candidate is silently counted as measured.

Estimated time:

- 4-10 hours.

## Goal4637. CuPy Partner Validation Or Explicit V4.0 Exclusion

Purpose:

- resolve whether CuPy is part of formal V4.0 measured scope.

Tasks:

- run CuPy validation gates for already measured surfaces where feasible;
- require parity and performance evidence;
- otherwise keep CuPy fail-closed and remove it from V4.0 release wording.

Exit gate:

- either CuPy has measured evidence for specific surfaces;
- or V4.0 release wording explicitly says Torch CUDA only.

Estimated time:

- 2-6 hours depending on POD CuPy environment.

## Goal4638. Formal Release Scorecard Freeze

Purpose:

- freeze the exact release scorecard before all-app/promoted benchmark runs.

Tasks:

- define benchmark families included/excluded;
- define measured surfaces included/excluded;
- define baselines;
- define performance thresholds;
- define parity thresholds;
- define allowed public wording for pass/fail outcomes.

Exit gate:

- no benchmark classification may change after results are seen;
- scorecard is reviewable by external AIs before the run.

Estimated time:

- 1-2 hours, no POD.

## Goal4639. Serious All-App / Promoted Benchmark POD Gate

Purpose:

- produce release-grade evidence, not toy evidence.

Tasks:

- run the frozen scorecard from Goal4638 on POD;
- include all promoted benchmark families that are in V4.0 scope;
- record excluded/deferred rows explicitly;
- collect raw timings, medians, repeats, parity, hardware/software metadata.

Exit gate:

- results are complete, or every incomplete row has a hard failure reason;
- geomean and per-family results are computed according to frozen rules;
- no broad wording is inferred beyond the evidence.

Estimated time:

- 4-12 POD hours depending on benchmark breadth.

## Goal4640. User-Facing V4 Cleanup

Purpose:

- make users see one clean V4 surface, not internal history.

Tasks:

- update front page;
- update `future/v4/README.md`;
- update tutorials and examples;
- hide or clearly fence historical/candidate details;
- ensure every visible example runs or is marked as environment-gated.

Exit gate:

- users can understand what V4 supports today;
- candidate/deferred/Tier-3 surfaces cannot be mistaken for supported release
  features;
- example smoke tests pass.

Estimated time:

- 3-6 hours.

## Goal4641. Clean-Tree Reproducibility Gate

Purpose:

- prove release artifacts are reproducible from a clean workspace.

Tasks:

- collect intended files;
- remove or archive temporary churn artifacts;
- run local tests;
- run required POD smoke/release gates from clean checkout or clean branch;
- record exact commands and outputs.

Exit gate:

- clean-tree test pass;
- no untracked temporary artifact is required for release;
- release package can be regenerated.

Estimated time:

- 2-5 hours.

## Goal4642. Final 3-AI Release Review Packet

Purpose:

- obtain explicit release authorization or explicit no-go.

Tasks:

- prepare final packet with:
  - scope;
  - measured operators;
  - benchmark results;
  - coverage split;
  - docs/examples status;
  - forbidden claims;
  - release notes.
- request 3-AI review:
  - Claude;
  - Antigravity;
  - Codex/main AI or another available independent reviewer if the owner
    provides one.

Exit gate:

- formal verdict is one of:
  - `authorize_formal_high_performance_v4_release`;
  - `authorize_bounded_operator_v4_release_only`;
  - `block_release_required_fixes`;
  - `reject_release_reframe_needed`.

Estimated time:

- 2-8 hours depending on reviewer availability.

## Goal4643. Formal V4 Release Publication

Purpose:

- publish only after Goal4642 authorizes a release.

Tasks:

- update final version files;
- update release notes;
- tag or prepare release commit;
- ensure public docs contain only authorized claims;
- preserve history in history/future folders where appropriate.

Exit gate:

- release label matches authorization;
- no forbidden claim appears in user-facing docs;
- all final tests pass.

Estimated time:

- 1-3 hours.

## Goal4644. Post-Release Guardrails

Purpose:

- prevent regression into the V3/V4 confusion pattern.

Tasks:

- add tests/gates that reject:
  - candidate surfaces counted as measured;
  - broad speedup wording without all-app gate;
  - CuPy claims without CuPy evidence;
  - Tier-3 support claims while Tier-3 remains spike/deferred;
  - old/history docs appearing in the user front door.

Exit gate:

- guardrail tests pass;
- future releases cannot silently widen claims.

Estimated time:

- 2-4 hours.

## Critical Path Summary

Minimum path to formal high-performance V4:

1. Goal4633 weighted-sum decision.
2. Goal4634 coverage refresh.
3. Goal4635 and Goal4636 coverage expansion.
4. Goal4638 scorecard freeze.
5. Goal4639 serious POD all-app/promoted benchmark gate.
6. Goal4640 docs/examples cleanup.
7. Goal4641 clean-tree reproducibility.
8. Goal4642 3-AI final release authorization.
9. Goal4643 publication.

Goal4637 CuPy validation can run in parallel, but if it does not pass, V4.0
release wording must explicitly remain Torch CUDA only.

## Non-Authorization

This roadmap does not authorize:

- V4 release;
- V4 release-candidate status;
- broad speedup claims;
- whole-app speedup claims;
- CuPy performance claims;
- Tier-3 callback support;
- true-zero-copy public wording;
- C ABI / embedding / non-Python host claims;
- app-specific native kernels.

## Goal-Level Decision Self-Audit

Decision: write the formal V4 release-hardening goals before executing them.

1. Am I being foolish?
   - No. This prevents the next work from becoming disconnected micro-goals.

2. What actions would make this foolish?
   - Treating this roadmap as release authorization.
   - Running all-app benchmarks before the scorecard is frozen.
   - Continuing only weighted-sum while ignoring coverage, docs, and final
     release review.

3. Is there another path that avoids being stuck on one idea?
   - Yes. If weighted-sum fails, the roadmap continues by excluding/rejecting it
     and expanding coverage through other generic operators.

4. Can I start a different path that truly solves the problem?
   - Yes. After owner review, the real path is engineering release-hardening:
     measured operator coverage, serious benchmarks, clean docs, clean tree, and
     final 3-AI authorization.
