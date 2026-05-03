# Goal1229 Two-AI Consensus

Date: 2026-05-03

Participants:

- Codex, primary implementer/reviewer
- Gemini CLI, external reviewer

## Scope

Goal1229 adds a current-main v1.0 readiness audit that is separate from the
historical `v0.9.8` release package and tag boundary.

The audit checks that current main:

- has 12 reviewed bounded RTX sub-path public wording rows;
- keeps `graph_analytics` and `polygon_pair_overlap_area_rows` blocked for
  positive public speedup wording;
- keeps `database_analytics` and `polygon_set_jaccard` not reviewed for public
  speedup wording;
- excludes `apple_rt_demo` and `hiprt_ray_triangle_hitcount` from NVIDIA public
  wording targets;
- keeps stale Goal1208/11-row current-main wording out of the public docs;
- preserves the v1.0/v1.5/v2.0 positioning from Goal1228.

## Consensus

VERDICT: ACCEPT

Codex and Gemini agree that the Goal1229 audit is technically bounded and useful
for v1.0 release-readiness work. It improves current-main discipline without
retconning the released `v0.9.8` package and without authorizing any new release
or whole-app speedup claim.

No required fixes remain for this bounded audit goal.

## Verification

Gemini external review:

- `docs/reports/goal1229_gemini_current_main_v1_0_readiness_audit_review_2026-05-03.md`

Local regression tests:

- `PYTHONPATH=src:. python3 -m unittest tests.goal1229_current_main_v1_0_readiness_audit_test -v`
