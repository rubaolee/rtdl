# Goal684 External Review — Claude

Date: 2026-04-21

Verdict: **ACCEPT**

## Scope Reviewed

- `docs/reports/goal684_v0_9_6_release_level_flow_audit_2026-04-21.md`
- `docs/release_reports/v0_9_6/README.md`, `release_statement.md`, `support_matrix.md`, `audit_report.md`
- `README.md`, `docs/README.md`, `docs/current_main_support_matrix.md`, `docs/quick_tutorial.md`,
  `docs/release_facing_examples.md`, `examples/README.md`, `docs/features/README.md`,
  `docs/rtdl_feature_guide.md`, `docs/tutorials/README.md`, `docs/backend_maturity.md`

## Public Doc Staleness Check

All ten public docs and the four v0.9.6 release package docs are internally consistent.
No stale "candidate" wording was found. Every doc correctly states:

- Current released version: `v0.9.6`.
- v0.9.5 retained as the prior any-hit / visibility-row / `reduce_rows` release.
- v0.9.6 scoped to prepared/prepacked repeated visibility/count optimizations
  plus native/native-assisted any-hit completion for Vulkan and Apple RT.
- Scalar/compact output contracts distinguished from full emitted-row output throughout.
- Required non-claims consistently enforced: no broad DB/graph/one-shot speedup,
  no AMD GPU HIPRT validation, no GTX 1070 RT-core speedup, no Apple MPS RT
  DB/graph traversal, no Apple full emitted-row speedup, no `reduce_rows` native
  backend acceleration.

No stale public-doc claim blocks release.

## Multi-AI Flow Check

Every goal group in the v0.9.6 chain has at least two-AI review coverage.
No single-developer-only gate was found:

- Goals 650–653, 654–657, 675: explicitly accepted by 2 AI (Codex + Gemini Flash);
  Claude was unavailable or stalled and is not counted — the audit correctly
  reports 2-AI acceptance rather than falsely claiming 3-AI consensus.
- Goals 658–684 (major closure, optimization, gate, and release goals): accepted
  by 3-AI consensus (Codex + Claude + Gemini Flash), with Goal684 itself
  receiving Codex acceptance and this external Claude review as the second vote.

The minimum release policy (≥ 2 AI for all goals, 3-AI consensus for important
planning and release gates) is met throughout.

## Test Evidence

- Full local discovery after release packaging: **1274 tests OK, 187 skips**.
- Public command truth audit: valid, **250 commands across 14 docs**.
- Public entry smoke: valid.
- Focused public release-doc tests: 20 tests OK.
- Linux fresh backend gate: OptiX, Vulkan, and HIPRT build and focused native
  suite (30 tests OK) pass on the GTX 1070 host.
- `git diff --check`: clean.

Test evidence is consistent across the flow audit, support matrix, audit report,
and release package README.

## Release Non-Claim Verification

All required non-claims from the audit are present and consistently worded in
every reviewed document. No document makes a disallowed claim.

## Verdict Rationale

The release surface is precisely bounded, all public docs reflect the v0.9.6
boundary, test gates are met, and no single-developer-only action exists in the
release chain. No blocker was found.
