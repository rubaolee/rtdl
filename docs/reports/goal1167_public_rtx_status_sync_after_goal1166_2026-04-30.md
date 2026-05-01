# Goal1167 Public RTX Status Sync After Goal1166

Date: 2026-04-30

## Scope

Synchronize the public v1.0 RTX status docs after the Goal1164 RTX A5000 batch,
Goal1165 local ANN/robot/Jaccard fixes, and Goal1166 accepted next-pod packet.

This goal is documentation and status-surface sync only. It does not promote any
new public speedup wording.

## Changes

- Updated `scripts/goal947_v1_rtx_app_status_page.py` so generated
  `docs/v1_0_rtx_app_status.md` records:
  - Goal1164 RTX A5000 smoke/medium batch completion.
  - Goal1165 local follow-up fixes for ANN, robot, and Jaccard.
  - Goal1166 Codex+Gemini accepted next-pod packet.
- Regenerated `docs/v1_0_rtx_app_status.md` and
  `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`.
- Updated `src/rtdsl/app_support_matrix.py` cloud-policy strings so the
  machine-readable maturity matrix names Goal1164-Goal1166 while preserving
  public wording boundaries.
- Updated `docs/app_engine_support_matrix.md` so user-facing matrix text no
  longer stops at Goal1136/Goal1146.
- Added regression coverage to
  `tests/goal947_v1_rtx_app_status_page_test.py` to require Goal1164-Goal1166
  context and to forbid accidental promotion to an 11th public wording row.

## Boundaries

- Reviewed public RTX wording remains `10` rows.
- Goal1164-Goal1166 are engineering, validation, and next-pod-preparation
  evidence only.
- No whole-app speedup, default-mode speedup, Python-postprocess speedup, or
  broad RT-core acceleration claim is authorized by this sync.
- `--skip-validation` timing artifacts remain timing-only and are not
  correctness evidence.

## Required External Review

This goal requires 2-AI consensus before closure. Gemini review should verify
that the public docs are current and that no new public speedup wording was
introduced.
