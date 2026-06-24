# Goal 63 Plan

Date: 2026-04-04

## Why This Goal Exists

The repo now has a live audit policy in `docs/audit_flow.md`, but the policy
itself should be exercised once in a full real audit round instead of existing
only as guidance text.

## Planned flow

1. publish the live audit-flow policy into the canonical docs surface
2. run a fresh verification baseline
3. perform a Codex audit against:
   - code
   - docs
   - code/doc consistency
   - history/archive consistency
   - manuscript source and PDF
4. request Gemini audit with the same scope
5. request Claude audit with the same scope if Claude is available
6. compare findings and correct any blocking issues
7. record the final consensus and publish only after the required rule is met

## Current consensus rule

- target: 3-AI consensus
- fallback if Claude is quota-blocked or unavailable:
  - Codex + Gemini consensus

## Working principle

This round should not invent new feature work. It should focus on whether the
current accepted RTDL state is internally trustworthy under the new audit-flow
contract.
