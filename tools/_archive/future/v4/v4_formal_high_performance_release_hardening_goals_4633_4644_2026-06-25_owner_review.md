# V4 Formal High-Performance Release-Hardening Goals 4633-4644

Date: 2026-06-25

Status: `superseded_by_goal4633_4644_completion_audit`

Current valid public state after completion:

- `RTDL v4.0.0 formal high-performance generic RT-core operator release`

Completion record:

- `future/v4/v4_goal4633_4644_completion_audit_2026-06-25.md`

Original target:

- a formal high-performance V4 release only if the release-hardening gates below
  pass and final 3-AI authorization explicitly approves it.

This file turns the owner's mandatory route into an auditable goal list:

1. clear current review debt;
2. expand measured operator coverage;
3. handle/promote/reject the weighted-sum candidate;
4. run serious all-app / promoted benchmark release gates;
5. unify user-facing docs/examples into formal V4;
6. obtain 3-AI final release authorization;
7. publish only after authorization.

Non-negotiable boundaries:

- no broad V4 speedup claim before the serious release scorecard passes;
- no toy benchmark evidence may be used as release evidence;
- no candidate surface may be counted as measured;
- no CuPy claim without CuPy evidence;
- no Tier-3 arbitrary-callback claim while Tier-3 remains spike/deferred;
- no C ABI / embedding / non-Python-host claim in this V4.0 release path.

## Current Facts Before Owner Review

Goal4633 has already produced POD evidence and a Claude approval for measured
Torch CUDA promotion of weighted sum:

- evidence:
  `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json`
- decision:
  `future/v4/v4_goal4633_weighted_sum_promotion_decision_2026-06-25.md`
- Claude review:
  `future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_completion_review_2026-06-25.md`
- Antigravity review debt:
  `future/v4/reviews/antigravity_v4_goal4633_weighted_sum_promotion_completion_review_blocked_2026-06-25.md`

Goal4634 has been started as a coverage refresh after weighted-sum promotion:

- draft/current artifact:
  `future/v4/v4_goal4634_coverage_audit_refresh_after_weighted_sum_2026-06-25.md`

The owner may accept these as already executed facts or require re-review before
the remaining goals proceed.

## Goal4633. Weighted-Sum Candidate Promotion Gate

Purpose:

- resolve `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`;
- decide whether it becomes a measured Torch CUDA Tier-2 surface, remains
  candidate, or is rejected for V4.0.

Required tasks:

- use the amended wording:
  `same-operator comparable-route comparison`;
- run or accept the predeclared POD gate:
  shapes `32768`, `131072`, `262144`, `524288`;
  warmups `5`; repeats `30`; Torch CUDA only;
- record parity, ratios, geomean, hardware/software metadata, and hot-path
  device-residency metadata;
- update catalog/docs/tests only if promotion is justified.

Current result to audit:

- `promote_weighted_sum_measured_torch_v4_tier2`;
- ratio range: `1.2011x-2.1459x`;
- geomean: `1.5457x`;
- caveat: this is a bounded comparable-route win, not a broad app speedup.

Exit gate:

- owner accepts the evidence and review record, or orders rework;
- Antigravity debt remains recorded unless a later review closes it.

POD:

- already used; rerun only if owner/reviewer rejects evidence.

## Goal4634. Coverage Audit Refresh After Weighted-Sum

Purpose:

- update the V4 operator/app coverage split after Goal4633;
- identify the next measured-coverage blockers that can be moved by generic
  fused operators.

Required tasks:

- update `src/rtdsl/v4_coverage_audit.py`;
- update release-decision blockers/counts;
- classify each benchmark family as strong measured, partial measured,
  candidate, or deferred;
- name at least two next candidate blockers for generic-operator coverage work.

Exit gate:

- coverage split is current and test-backed;
- every remaining partial/deferred row has a next action;
- no broad V4 release claim is introduced.

Review:

- completion should go to Claude and Antigravity, or be recorded as review debt
  if a reviewer/tool is unavailable.

Estimated time:

- 1-2 hours from the current draft state.

## Goal4635. First New Generic Operator Coverage Expansion

Purpose:

- move one current partial/deferred benchmark family by adding or promoting one
  generic Tier-2 operator surface.

Allowed:

- generic continuation/push-down operators such as component union,
  ranked/top-k summary, AABB/relation prefilter, grouped reduction variants,
  nearest-witness variants, or other app-agnostic relation/reduction operators.

Forbidden:

- application-identity kernels such as a DBSCAN kernel, Barnes-Hut kernel,
  RayJoin kernel, triangle-counting kernel, or librts-specific kernel.

Required tasks:

- predeclare the target coverage row and operator hypothesis;
- implement/expose the generic operator surface;
- run correctness parity and POD performance gate;
- update catalog/coverage/docs/tests only if the gate passes.

Exit gate:

- one named coverage row moves with measured evidence, or the candidate is
  rejected with recorded evidence;
- gain source is operator/runtime-level, not app-specific route code.

Estimated time:

- 4-10 hours.

## Goal4636. Second New Generic Operator Coverage Expansion

Purpose:

- prove Goal4635 was not a one-off by moving a second coverage blocker under
  the same generic-operator rules.

Required tasks:

- select a second blocker, preferably a different continuation class;
- predeclare parity/performance thresholds;
- run POD gate;
- update catalog/coverage/docs/tests only if measured evidence supports it.

Exit gate:

- second named coverage row moves or is rejected with evidence;
- measured operator coverage improves beyond Goal4634;
- no candidate is silently promoted.

Estimated time:

- 4-10 hours.

## Goal4637. CuPy Partner Validation Or Formal V4.0 Exclusion

Purpose:

- decide whether CuPy is in formal V4.0 measured scope.

Required tasks:

- inspect/install CuPy only if POD environment and dependency risk are
  acceptable;
- run CuPy parity/performance gates for feasible measured surfaces;
- otherwise explicitly mark V4.0 as Torch CUDA measured scope only.

Exit gate:

- either CuPy has specific measured-surface evidence;
- or all user-facing docs and claim boundaries say CuPy is excluded/deferred
  for V4.0.

Estimated time:

- 2-6 hours depending on POD environment.

## Goal4638. Formal Release Scorecard Freeze

Purpose:

- freeze the exact release scorecard before serious all-app/promoted benchmark
  execution.

Required tasks:

- define included/excluded benchmark families;
- define measured operators included/excluded;
- define baselines and hardware;
- define performance thresholds;
- define correctness/parity thresholds;
- define allowed wording for pass/fail outcomes.

Exit gate:

- no benchmark classification can change after results are seen;
- scorecard is ready for external review before POD spend.

Review:

- Claude + Antigravity review required before Goal4639.

Estimated time:

- 1-2 hours.

## Goal4639. Serious All-App / Promoted Benchmark POD Gate

Purpose:

- produce release-grade performance evidence across the frozen promoted V4
  scope.

Required tasks:

- run the frozen Goal4638 scorecard on the same RT hardware class;
- include all in-scope promoted benchmark families;
- record every excluded/deferred row explicitly;
- collect raw timings, medians, repeats, parity, metadata, and failure reasons.

Exit gate:

- results are complete, or incomplete rows have hard failure reasons;
- geomean and per-family results are computed by the frozen rules;
- no broad wording is inferred beyond the measured evidence.

POD:

- required.

Estimated time:

- 4-12 POD hours depending on benchmark breadth and reruns.

## Goal4640. User-Facing V4 Documentation And Example Cleanup

Purpose:

- make the public V4 surface simple, unified, and not frightening to users.

Required tasks:

- clean front page / V4 README / catalog docs / tutorials / examples;
- hide or fence historical/development-only material;
- ensure every visible example runs or is clearly environment-gated;
- remove stale candidate wording after Goal4633/4634 updates;
- ensure public text matches the scorecard outcome.

Exit gate:

- a user sees one coherent V4 story;
- candidate/deferred/Tier-3 surfaces cannot be mistaken for release features;
- example smoke tests pass.

Estimated time:

- 3-6 hours.

## Goal4641. Clean-Tree Reproducibility Gate

Purpose:

- prove the formal V4 artifact can be regenerated from a clean repo state.

Required tasks:

- collect intended files;
- archive or remove temporary churn artifacts from the user front door;
- run local test suite for V4;
- run required POD smoke/release gates from a clean checkout or clean branch;
- record exact commands and outputs.

Exit gate:

- clean-tree validation passes;
- no untracked temporary file is required for release;
- release package can be regenerated.

Estimated time:

- 2-5 hours.

## Goal4642. Final 3-AI Release Authorization Packet

Purpose:

- obtain explicit release authorization or explicit no-go.

Required packet contents:

- scope;
- measured operators;
- scorecard/all-app results;
- coverage split;
- docs/examples status;
- review-debt status;
- forbidden claims;
- release notes;
- exact publication label being requested.

Exit verdict must be one of:

- `authorize_formal_high_performance_v4_release`;
- `authorize_bounded_operator_v4_release_only`;
- `block_release_required_fixes`;
- `reject_release_reframe_needed`.

Review:

- 3-AI required:
  Claude, Antigravity, and Codex/internal or another owner-provided reviewer.

Estimated time:

- 2-8 hours depending on reviewer availability.

## Goal4643. Formal V4 Publication

Purpose:

- publish only after Goal4642 authorizes a release.

Required tasks:

- update final version files;
- update release notes;
- tag or prepare release commit;
- ensure public docs contain only authorized claims;
- preserve historical/internal material outside the user front door.

Exit gate:

- release label matches authorization;
- no forbidden claim appears in user-facing docs;
- final tests pass.

Estimated time:

- 1-3 hours.

## Goal4644. Post-Release Guardrails

Purpose:

- prevent recurrence of V3/V4 confusion and candidate-overclaiming.

Required tasks:

- add/update tests that reject:
  candidate surfaces counted as measured;
  broad speedup wording without all-app gate;
  CuPy claims without CuPy evidence;
  Tier-3 support claims while Tier-3 remains spike/deferred;
  old/history docs appearing in the user front door;
  release docs that omit benchmark/parity caveats.

Exit gate:

- guardrail tests pass;
- future releases cannot silently widen claims.

Estimated time:

- 2-4 hours.

## Review And Execution Policy

- This file is for owner review first.
- After owner approval, execution starts at the first non-accepted goal.
- Major decisions and Goal4638/4639/4642 require external AI review before
  release claims.
- Goal completion should be reviewed by Claude and Antigravity when available;
  unavailable reviewers must be recorded as explicit review debt, not silently
  ignored.

## Resource Estimate

Minimum path if evidence holds:

- engineering: 20-45 hours;
- POD: 6-18 hours;
- reviews: 3-8 review interactions plus final 3-AI authorization.

High-risk path if coverage or all-app gates fail:

- engineering: 40+ hours;
- POD: 20+ hours;
- result may be a bounded operator V4 release or a blocked/no-go decision,
  not a formal high-performance release.
