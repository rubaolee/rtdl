# RTDL v0.1 Closure Execution Map

Date: 2026-04-05
Status: planned

## Purpose

This document turns Goals 93-96 into a concrete v0.1 closure sequence.

The main point is:

- v0.1 no longer needs another backend-capability proof
- v0.1 now needs release closure, release validation, release docs, and final
  release audit

## Goal stack

### Goal 93: reproduction closure package

Purpose:

- freeze the accepted RayJoin-style evidence into one release-facing package

Primary outputs:

- canonical closure report
- evidence manifest / summary JSON
- explicit skipped/unavailable surface list
- short reproduction runbook

Key honesty rules:

- bounded v0.1 package remains the trust anchor
- strongest performance claims remain the long exact-source `county_zipcode`
  positive-hit `pip` surface
- timing boundaries stay separate
- Vulkan remains parity-clean but slower
- overlay remains an overlay-seed analogue

### Goal 94: release validation

Purpose:

- rerun the smallest high-signal release-head validation package

Primary outputs:

- release-validation report
- release-validation artifact checklist
- pass/fail summary for local, Linux, artifact, and doc/result integrity

Recommended local validation:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal76_runtime_prepared_cache_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal91_backend_boundary_support_test

PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views
```

Recommended Linux validation:

```bash
cd /home/lestat/work/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_vulkan_test \
  tests.goal85_vulkan_prepared_exact_source_county_test

python3 scripts/goal51_vulkan_validation.py \
  --output build/goal94_goal51_validation/summary.json
```

Additional Linux release-head checks should reuse the accepted OptiX/Embree
surfaces from Goals 82 and 83 instead of inventing a new larger rerun.

### Goal 95: release docs

Purpose:

- convert the current evidence into one coherent release-facing reader path

Primary outputs:

- `docs/v0_1_release_notes.md`
- `docs/v0_1_reproduction_and_verification.md`
- `docs/v0_1_support_matrix.md`
- refreshed `README.md`
- refreshed `docs/README.md`

Required doc corrections:

- align top-level README and v0.1 plan with the newer long exact-source backend
  closure
- keep the bounded package visible as the trust anchor
- stop treating older feature/rayjoin target docs as canonical release status
  unless refreshed

### Goal 96: final v0.1 release audit

Purpose:

- run the final claim-consistency and release-integrity audit

Primary outputs:

- final release audit report
- findings list or explicit no-findings verdict
- final 2+ AI release consensus record

Audit focus:

- cross-doc consistency
- artifact/file existence and date/path correctness
- parity/performance language matches Goal 89 and related accepted artifacts
- oracle, Vulkan, and API-limit wording is consistent everywhere
- no stale internal wording remains in live docs

## Recommended execution order

1. Goal 93
2. Goal 95
3. Goal 94
4. Goal 96

Reason:

- Goal 93 defines the frozen release evidence surface
- Goal 95 makes the release story readable
- Goal 94 validates the actual release head that now includes those docs/tests
- Goal 96 audits the finished release package, not a partial one

## AI review assignment

Default pair for each goal:

- Codex
- Gemini

Claude:

- use as extra review or fallback when responsive
- especially useful for code-heavy review slices

## Current project position

Already complete before Goals 93-96:

- OptiX performance closure
- Embree performance closure
- Vulkan correctness/support closure
- oracle trust envelope
- milestone audit/test/doc package from Goals 90-92

So the remaining v0.1 work is now mostly:

- packaging
- validation
- documentation
- final audit
