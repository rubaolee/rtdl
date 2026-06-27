# V4 Formal High-Performance Release Goals For Owner Review

Date: 2026-06-25

Status: `owner_review_superseded_by_goal4633_4644_completion_audit`

This file converted the mandatory V4 release-hardening command into a concrete,
auditable goal list. Execution has since proceeded through the Goal4633-4644
completion chain. The current controlling completion record is:

- `future/v4/v4_goal4633_4644_completion_audit_2026-06-25.md`

This file remains as the owner-review planning record; it is not the current
completion proof by itself.

Mandatory command being captured:

1. clear review debt;
2. expand measured operator coverage;
3. handle the weighted-sum candidate;
4. run serious all-app / promoted benchmark release gate;
5. unify user documentation into formal V4;
6. obtain 3-AI final release authorization;
7. publish formal V4 only if the gates pass.

## Controlling Rule

RTDL V4 is a formal high-performance release only if the measured generic
RT-core operator surfaces, benchmark gates, public docs, and independent review
records all agree. Do not infer broad whole-application speedup, arbitrary
callback support, CuPy support, Tier-3 support, C ABI/embedding support, or
non-Python host support unless a specific later goal proves and authorizes that
claim.

## Decision Self-Audit

1. Was this decision stupid?
   - No, if it stays a plan file for owner review and does not silently execute
     or authorize release.
2. What actions would make it stupid?
   - Treating the plan as proof; counting candidates as measured surfaces;
     running benchmark gates before scorecard freeze; or publishing wording that
     outruns evidence.
3. Is there another path that avoids being stuck on a wrong idea?
   - Yes. Every performance goal has a reject/defer branch; failed candidates
     must be recorded honestly rather than forced into release.
4. Can we switch to a real problem-solving path?
   - Yes. Progress is defined by closed review debt, promoted measured operator
     surfaces, serious scorecard evidence, clean public docs, and explicit
     3-AI authorization.

## Goal4633. Weighted-Sum Promotion Or Rejection Gate

Purpose:

- resolve `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`;
- decide whether it is promoted to measured V4 Tier-2 surface, kept candidate,
  or rejected/deferred for V4.0.

Exit evidence:

- frozen promotion criteria before judging results;
- parity at all measured shapes;
- per-shape timings, repeats, hardware/software metadata, and geomean;
- catalog/docs/tests updated if promoted;
- explicit candidate/deferred/rejected wording if not promoted.

Forbidden:

- do not count weighted-sum as measured release coverage before it passes;
- do not describe the result as broad triangle-counting or whole-app speedup.

Review:

- goal completion requires 3-AI consensus where available, or recorded review
  debt for unavailable reviewers.

## Goal4634. Coverage Audit Refresh After Weighted-Sum Decision

Purpose:

- refresh the V4 operator coverage table after Goal4633;
- identify which benchmark families are strong measured, partial measured,
  candidate, deferred, or out of V4.0 scope.

Exit evidence:

- updated coverage audit source and tests;
- every non-strong row has a next action or explicit V4.0 exclusion;
- no old candidate/deferred row is silently counted as measured.

Forbidden:

- do not publish workload coverage percentages without the audited table.

## Goal4635. Expand Measured Operator Coverage: First Generic Blocker

Purpose:

- promote or reject one additional generic Tier-2 operator that moves a real
  coverage blocker.

Allowed:

- generic continuation or push-down operators, such as component union,
  grouped reduction, nearest witness, threshold summary, AABB/index prefilter,
  ranked/top-k summary, min/max/count/sum-style reductions.

Forbidden:

- app-identity kernels such as DBSCAN, Barnes-Hut, RayJoin, triangle-counting,
  or LibRTS-specific kernels.

Exit evidence:

- predeclared operator hypothesis;
- parity proof;
- POD or equivalent serious hardware performance evidence;
- catalog/docs/tests updated only if the gate passes;
- win source classified as runtime/operator-level, not app-specific patching.

## Goal4636. Expand Measured Operator Coverage: Second Generic Blocker

Purpose:

- prove Goal4635 was not a one-off by moving another coverage blocker under
  the same generic-operator rule.

Exit evidence:

- second named blocker moves, or is rejected with evidence;
- the two coverage wins do not rely on the same narrow trick unless the release
  wording says so;
- coverage audit and public catalog remain synchronized.

## Goal4637. Partner Scope Decision

Purpose:

- decide exactly which Python GPU partners are part of formal V4.0 measured
  scope.

Exit evidence:

- Torch CUDA support is recorded per measured surface;
- CuPy/Numba support is either validated per surface or explicitly excluded
  from V4.0 public claims;
- partner-specific failures are fail-closed, not softened in wording.

Forbidden:

- no public CuPy performance/support claim without surface-specific evidence.

## Goal4638. Formal Release Scorecard Freeze

Purpose:

- freeze the serious release scorecard before any release benchmark run.

Exit evidence:

- included surfaces, excluded surfaces, baselines, parity thresholds,
  performance thresholds, repeats, warmups, hardware metadata, and public
  wording rules are frozen before results are inspected;
- scorecard classification cannot be changed after seeing results.

Forbidden:

- no all-app / promoted benchmark release gate before this freeze is reviewed.

Review:

- external review is required before Goal4639 starts.

## Goal4639. Serious All-App / Promoted Benchmark Release Gate

Purpose:

- produce release-grade evidence across the frozen promoted V4 scorecard.

Exit evidence:

- all included scorecard rows complete, or every missing row has a hard failure
  reason;
- raw results, medians, ratios, parity, repeats, metadata, and evaluator output
  are archived;
- scorecard pass/fail is computed by the frozen Goal4638 rules;
- public wording is bounded to measured surfaces and exact scorecard result.

Forbidden:

- no toy-size-only result;
- no retrospective scorecard edits;
- no broad V4-vs-V2.x or whole-app speedup claim unless the frozen scorecard
  explicitly supports it.

## Goal4640. User-Facing V4 Documentation Cleanup

Purpose:

- make the public front door clean, unified, current, and not frightening to
  users.

Exit evidence:

- root README, current status docs, V4 README, catalog docs, performance wording
  docs, tutorials, and visible examples agree on the same V4 state;
- old V3/V4 churn is fenced away from the user path;
- visible examples either run directly or are clearly environment-gated;
- candidate/deferred/Tier-3/internal details cannot be mistaken for supported
  V4.0 features.

Forbidden:

- no stale "development preview" wording if release is authorized;
- no release wording if final authorization has not happened.

## Goal4641. Clean-Tree Reproducibility Gate

Purpose:

- prove the release state is reproducible from a clean checkout, not from local
  accidental files.

Exit evidence:

- clean-tree checkout or clean worktree validation;
- full V4 test suite pass;
- release examples and scorecard dry-run pass;
- no untracked temporary artifact is required for the release state.

Forbidden:

- no release publication from a dirty-only state.

## Goal4642. Final 3-AI Release Authorization

Purpose:

- obtain explicit independent authorization to publish formal V4.0, or record
  explicit no-go.

Packet must include:

- scope;
- measured operators;
- benchmark scorecard result;
- coverage split;
- partner scope;
- docs/examples status;
- forbidden claims;
- clean-tree reproducibility evidence;
- exact requested release label.

Exit evidence:

- three independent AI seats authorize the bounded formal release, or a missing
  reviewer is recorded as review debt only if enough independent seats remain
  and the owner accepts that process;
- all amendments requested by reviewers are closed before publication.

Forbidden:

- no release if final reviewers authorize only a preview/development state.

## Goal4643. Publication Patch

Purpose:

- convert the authorized release decision into the actual public V4 state.

Exit evidence:

- version metadata updated;
- V4 front door reports the authorized release label;
- scope/catalog/docs/examples agree;
- broad forbidden claims remain blocked in code and docs;
- targeted and full V4 tests pass.

Forbidden:

- publication must not expand scope beyond Goal4642 authorization.

## Goal4644. Post-Release Guardrails And Debt Ledger

Purpose:

- keep V4 honest after publication and prevent drift back into overclaiming.

Exit evidence:

- post-release guardrail tests cover release label, docs caveats, forbidden
  claims, scorecard references, and future-work boundaries;
- any deferred Claude/Antigravity review debt is listed with status and owner;
- next post-V4.0 goals are separated from V4.0 release claims.

Forbidden:

- do not reopen V4.0 release scope by adding V4.x items into V4.0 docs.

## Owner Review Questions

Please review these points before authorizing execution:

1. Is Goal4633 still the correct first numbered goal for this release-hardening
   chain, or should the list be renumbered?
2. Should CuPy validation remain a release blocker, or should V4.0 explicitly
   scope to Torch CUDA only?
3. Is the Goal4639 scorecard scope broad enough for a formal high-performance
   release while still avoiding whole-app overclaiming?
4. Is Goal4642 allowed to use recorded review debt if Claude is temporarily
   unavailable but two other independent review seats plus main-owner audit are
   available?

## Non-Authorization

This file does not authorize:

- formal V4 release;
- broad speedup claims;
- all-benchmark claims;
- whole-application speedup claims;
- public true-zero-copy claims;
- Tier-3 arbitrary callback support;
- raw OptiX callback API support;
- CuPy support;
- C ABI, embedding, non-Python host bindings, or V4.x scope.
