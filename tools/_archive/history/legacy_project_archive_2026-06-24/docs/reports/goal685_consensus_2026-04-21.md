# Goal685 Consensus: Engine Feature Support Contract

Date: 2026-04-21

Status: ACCEPT

## Scope

Goal685 adds a machine-readable and public documentation contract requiring
every public selectable RTDL feature to have an explicit support status on every
RTDL engine.

Allowed statuses:

- `native`
- `native_assisted`
- `compatibility_fallback`
- `unsupported_explicit`

## Review Inputs

- Codex implementation report:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal685_engine_feature_support_contract_2026-04-21.md`
- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal685_external_review_claude_2026-04-21.md`
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal685_external_review_gemini_flash_2026-04-21.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | ACCEPT | Implemented matrix, docs, exports, and regression tests. |
| Claude | ACCEPT | Verified 20 features x 5 engines, status limits, no blank cells, and preserved honesty boundaries. |
| Gemini Flash | ACCEPT | Returned ACCEPT on the requested external review. |

## Consensus

The 3-AI consensus is ACCEPT.

This change is suitable for post-`v0.9.6` mainline because it improves the
developer-facing support contract without broadening release performance
claims. Compatibility paths and native-assisted paths remain explicit states,
and silent CPU fallback is prohibited for advertised RT engine support.
