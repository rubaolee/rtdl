# 3-AI Consensus: Goal 1599 v1.6 Python+RTDL Readiness Boundary

## Verdict

Consensus is reached for the readiness boundary artifact.

`docs/reports/goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md`
is accepted as a safe planning and boundary document for `v1.6`.

This consensus does not authorize a `v1.6` release, stable `COLLECT_K_BOUNDED`
promotion, public speedup wording, true zero-copy wording, partner support
claims, package-install claims, or any release tag action.

## Reviewed Artifacts

- Codex readiness report:
  `docs/reports/goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md`
- Claude review:
  `docs/reviews/goal1599_v1_6_readiness_claude_review_2026-05-09.md`
- Gemini review:
  `docs/reviews/goal1599_v1_6_readiness_gemini_review_2026-05-09.md`

## Consensus Positions

Codex position:

`v1.6` should be treated as the first historical Python+RTDL closure milestone,
but current `main` is not ready to publish that closure. The correct boundary is
that RTDL accelerates the RT-shaped primitive/native backend portion and bridge
for Python caller code that invokes RTDL-managed RT primitives. RTDL does not
optimize arbitrary user Python code or whole applications.

Claude position:

Claude returned `ACCEPT` for the report as a readiness/boundary artifact, not
as release authorization. Claude found no overclaims and recommended three
wording improvements: tighten "supported Python applications," define
"compatibility/proof entry points," and clarify that the current evidence list
is foundation evidence rather than closure proof. Those edits were applied to
the report before this consensus file was written.

Gemini position:

Gemini endorsed the report's conclusion to proceed toward `v1.6` but not
publish yet. Gemini highlighted scope discipline, conservative
`COLLECT_K_BOUNDED` handling, the native-boundary audit, pod/no-pod work
separation, and reduced-copy versus true-zero-copy wording as the critical
release controls.

## Accepted Boundary

The accepted `v1.6` planning boundary is:

- Python remains the app/control/lowering layer.
- RTDL owns the RT-shaped primitive contract and bridge to native execution.
- Embree and OptiX are the active closure backends for the claimed surface.
- Stable native paths should be primitive-oriented, not app-name-oriented.
- Performance wording must name exact measured RT subpaths only.
- Python continuation, ETL, ranking, clustering, SQL behavior, graph-system
  analytics, exact refinement, and arbitrary Python code remain outside RTDL's
  optimization responsibility.

## Required Next Work

The next local work should be:

- write a formal `v1.6` release-surface proposal;
- audit docs for overclaims;
- audit native and Python wrapper names for stable-path app leakage;
- add blocked-claim regression tests;
- prepare a batched pod runbook before requesting GPU time.

## Decision

Proceed toward `v1.6` under this boundary.

Do not publish `v1.6` yet.
