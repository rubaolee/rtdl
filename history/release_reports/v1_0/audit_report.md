# RTDL v1.0 Release Audit Report

Status: released as `v1.0`.

Date: 2026-05-04

## Audit Scope

This audit records the evidence used to release v1.0 as an app-shaped RTDL
proof release.

The release package covers:

- front page and public documentation map;
- quick tutorial and tutorial index;
- app/example quickstart, application catalog, and v1.0 app acceleration
  inventory;
- architecture, programming model, IR/lowering, and performance docs;
- current RTX public wording status;
- explicit boundaries for blocked, not-reviewed, and non-NVIDIA rows;
- the v1.5 and v2.0 handoff meaning.

## Test Audit

Recent local evidence before this package:

- Goal1246 front-page diet focused suite: `55` tests OK.
- Goal1246 broader public-doc subset: `345` tests OK, `2` skipped.
- Goal1247 quick-tutorial focused suite: `12` tests OK.
- Goal1247 quick-tutorial related suite: `73` tests OK.
- Goal1247 broader public-doc subset: `345` tests OK, `2` skipped.
- Goal1251 full local discovery: `2422` tests OK, `196` skipped, `0`
  failures, `0` errors, `166.940s`.

Final release-action evidence:

- v1.0 release-candidate package tests passed before authorization;
- release-surface documentation audits passed before authorization;
- external-AI package review and Codex consensus were saved;
- final release authorization was saved before changing `VERSION` or tagging.

## Documentation Audit

The current public documentation separates:

- current released version `v1.0`;
- released v1.0 package status;
- v1.0 as foundation/proof release;
- v1.5 as generic primitive cleanup;
- v2.0 as end-to-end performance architecture;
- reviewed sub-path speedups from whole-app or all-app speedups;
- backend execution from public speedup authorization.

## Known Non-Claims

This release rejects these claims:

- all apps have public RTX speedup wording;
- all backends have equivalent support;
- app-specific native continuations are already gone;
- OptiX is always faster than Embree;
- v1.0 is the final v2.0 performance system.

## Audit Verdict

RTDL v1.0 is released as the app-shaped RTDL proof release. No immediate pod is required for the documented v1.0 proof scope. A pod is only needed if the scope
changes to promote blocked or not-reviewed app rows into new public speedup
claims.
