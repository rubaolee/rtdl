# RTDL v1.0 Release Candidate Audit Report

Status: draft release candidate for `v1.0`; not released.

Date: 2026-05-04

## Audit Scope

This audit checks whether current main is ready to enter final v1.0 release
review as an app-shaped RTDL proof release. It does not authorize a tag.

The release-candidate package covers:

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

Required before final release action:

- run the v1.0 release-candidate package tests;
- run release-surface documentation audits after any last docs edits;
- save external-AI package review and Codex consensus;
- save final release authorization before changing `VERSION` or tagging.

## Documentation Audit

The current public documentation separates:

- current released version `v0.9.8`;
- draft v1.0 release-candidate package status;
- v1.0 as foundation/proof release;
- v1.5 as generic primitive cleanup;
- v2.0 as end-to-end performance architecture;
- reviewed sub-path speedups from whole-app or all-app speedups;
- backend execution from public speedup authorization.

## Known Non-Claims

This release candidate rejects these claims:

- RTDL v1.0 is already released;
- all apps have public RTX speedup wording;
- all backends have equivalent support;
- app-specific native continuations are already gone;
- OptiX is always faster than Embree;
- v1.0 is the final v2.0 performance system.

## Audit Verdict

Current main is close to a v1.0 release candidate, but not yet a released v1.0.
No immediate pod is required for the documented v1.0 proof scope. A pod is only
needed if the release scope changes to promote blocked or not-reviewed app rows
into new public speedup claims.
