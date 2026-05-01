# Goal1220 Two-AI Consensus

Date: 2026-05-01

## Verdict

`ACCEPT`

## Participants

- Codex/main AI: wrote the final v0.9.8 authorization record and validation
  test.
- Gemini CLI: external reviewer. The saved review is
  `docs/reports/goal1220_gemini_v0_9_8_final_authorization_review_2026-05-01.md`.

## Evidence Accepted

- `docs/reports/goal1220_v0_9_8_final_authorization_2026-05-01.md`
- `docs/reports/goal1220_gemini_v0_9_8_final_authorization_review_2026-05-01.md`
- `tests/goal1220_v0_9_8_final_authorization_test.py`
- `docs/release_reports/v0_9_8/`

## Consensus

Goal1220 is accepted. The v0.9.8 release-action step is now authorized under
the documented boundary:

- public RTX wording remains bounded at `11` reviewed rows;
- the only newly reviewed row is
  `road_hazard_screening / prepared_native_compact_summary_40k`;
- `database_analytics` public speedup wording remains `blocked`;
- `polygon_set_jaccard` public speedup wording remains `blocked`;
- no broad app-suite, whole-app, or all-OptiX RT-core speedup claim is
  authorized;
- no additional pod run is required before the release action.

## Authorized Next Step

The next release-action step may:

1. bump `VERSION` from `v0.9.6` to `v0.9.8`;
2. run final focused release validation;
3. commit the release package and version bump;
4. create annotated tag `v0.9.8`;
5. push `main` and tag `v0.9.8`.

This consensus does not itself perform those actions.
