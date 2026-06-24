# 3-AI Consensus: Goal 1601 v1.6 Release-Surface Proposal

## Verdict

Consensus is reached.

Goal 1601 is accepted as the formal `v1.6` Python+RTDL release-surface
proposal artifact.

This consensus does not authorize `v1.6` release, release-tag action, stable
`COLLECT_K_BOUNDED` promotion, public speedup wording, whole-app speedup
wording, broad RTX/GPU acceleration wording, true zero-copy wording, partner
support claims, or package-install claims.

## Reviewed Artifacts

- Proposal:
  `docs/reports/goal1601_v1_6_release_surface_proposal_2026-05-09.md`
- Proposal tests:
  `tests/goal1601_v1_6_release_surface_proposal_test.py`
- Claude review:
  `docs/reviews/goal1601_v1_6_release_surface_proposal_claude_review_2026-05-09.md`
- Gemini review:
  `docs/reviews/goal1601_v1_6_release_surface_proposal_gemini_review_2026-05-09.md`

## Consensus Positions

Codex position:

`v1.6` should anchor the first Python+RTDL architecture milestone so the
project can stop being trapped only in minor optimization loops. This anchor
does not reduce the priority of performance work. NVIDIA RT-core performance,
`COLLECT_K_BOUNDED` optimization, reduced-copy/true-zero-copy evidence, and
OptiX work remain top engineering priorities after the anchor.

Claude position:

Claude returned `ACCEPT` for the proposal as a release-surface planning
artifact, not release authorization. Claude found no architecture-boundary or
performance overclaim. Claude recommended coupling the Included Surface section
to the Pending Or Excluded Surface section and adding a negative phrase guard
against accidental authorization language. Both hardening changes were applied
before this consensus file was written.

Gemini position:

Gemini supported the proposal as the definitive `v1.6` planning artifact.
Gemini agreed that `v1.6` should be a structural boundary rather than a
performance ceiling, and that public claims must remain strictly contained
until closure audits, validation, final 3-AI consensus, and explicit user
authorization are complete.

## Accepted Release-Surface Boundary

The accepted proposed `v1.6` surface is:

- Python remains the app/control layer.
- RTDL owns the RT-shaped primitive contract and bridge to native Embree/OptiX
  execution.
- The public claim is limited to reviewed RT primitive subpaths.
- RTDL does not claim to optimize arbitrary Python code or whole applications.
- OptiX is an active closure backend, but `--backend optix` alone is not a
  NVIDIA RT-core speedup claim.
- `COLLECT_K_BOUNDED` remains pending unless a separate reviewed gate promotes
  it.
- Performance work remains top priority after the architecture anchor.

## Remaining Closure Gates

Before `v1.6` can be published, these gates remain open:

- public docs overclaim audit;
- stable native-path app-leakage audit;
- blocked-claim regression test integration with the release package;
- Windows source-tree validation;
- Linux source-tree validation;
- real NVIDIA OptiX validation for the exact claimed surface;
- final release package with release statement and support matrix;
- final 3-AI release consensus;
- explicit user authorization for release/tag action.

## Validation

Windows proposal/readiness slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal1601_v1_6_release_surface_proposal_test `
  tests.goal1600_v1_6_python_rtdl_readiness_gate_test
```

Result:

- `Ran 9 tests`
- `OK`

## Decision

Accept Goal 1601 as the formal `v1.6` release-surface proposal artifact.

Proceed next to the public docs overclaim audit and stable native-path
app-leakage audit.

Do not publish `v1.6` yet.
