# Goal1228 Two-AI Consensus

Date: 2026-05-03

Participants:

- Codex, primary implementer/reviewer
- Gemini CLI, external reviewer

## Scope

Goal1228 updates the v1.0 public positioning and app-customization
documentation so current docs say:

- v1.0 validates the RTDL model on real application-shaped kernels, but is not
  the final generic/performance architecture.
- v1.0 public speedup claims are bounded reviewed sub-path claims, not whole-app
  or whole-class acceleration claims.
- The current public state after Goal1224 is 12 reviewed bounded RTX sub-path
  rows.
- Hausdorff is reviewed only for bounded prepared threshold-decision wording.
- `graph_analytics` and `polygon_pair_overlap_area_rows` remain public speedup
  wording blocked because same-contract evidence showed OptiX slower than
  Embree.
- App-specific native continuations are v1.0 proof machinery and must be
  replaced by reviewed generic primitives in v1.5.
- v2.0 targets broader end-to-end performance through explicit GPU compute and
  zero-copy partnership, not magic whole-program compilation.

## Consensus

VERDICT: ACCEPT

Codex and Gemini agree that the Goal1228 documentation updates are technically
bounded and release-directionally correct. The docs now distinguish the working
v1.0 proof surface from the planned v1.5 generic primitive refactor and v2.0
performance architecture.

No required fixes remain for this bounded documentation goal.

## Verification

Gemini external review:

- `docs/reports/goal1228_gemini_v1_0_positioning_docs_review_2026-05-03.md`

Local regression tests:

- `PYTHONPATH=src:. python3 -m unittest tests.goal947_v1_rtx_app_status_page_test tests.goal1228_v1_0_positioning_docs_test -v`
