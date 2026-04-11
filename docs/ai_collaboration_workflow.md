# RTDL AI Collaboration Workflow

This file summarizes the current multi-agent workflow used in RTDL.

Current authoritative rule source:

- `refresh.md` in the maintainer home directory remains the first file to re-read
  before substantial RTDL work after context loss or long sessions.

## Roles

### Codex

- primary implementation owner
- local code review
- final repo-state responsibility

### Gemini

- independent review
- scope critique
- cross-check on claims, consistency, and risk

### Claude

- independent review and, when requested, external implementation work
- must be reviewed before external code is allowed into the main repo

## Standard Loop

Typical round:

1. Codex defines the goal
2. Gemini and/or Claude review the goal or implementation
3. Codex revises or implements
4. reviewers check the result
5. consensus is recorded
6. only then is the result treated as accepted repo state

## Current Policy

- Codex controls the main repo
- external implementation work must be reviewed before merge
- the default closure rule is now stronger than generic "two AIs should agree":
  - saved Codex consensus is required
  - plus at least one saved Gemini or Claude review artifact
- when one reviewer is quota-blocked or unavailable, the fallback rule must be
  stated explicitly

## Why This Exists

The point is not ceremony.

The point is to reduce:

- silent correctness drift
- documentation over-claiming
- unreviewed backend changes
- goal closure based only on local optimism

## Boundary

This file is the live workflow summary, not the archive of every past review
round. Historical details remain in `history/`.

The stricter reviewer-accountability and audit-contract rules are documented in:

- `docs/audit_flow.md`
- `refresh.md`
