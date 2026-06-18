# RTDL Development Reliability Process

This document explains the current project rule for turning work into accepted
repo state.

## Purpose

RTDL is a research systems project with:

- language design
- multiple runtimes
- dataset handling
- experiment/report generation
- multi-agent review

So “the code runs” is not enough by itself.

## Current Standard

Every serious round should have:

1. an explicit goal
2. review before or around implementation
3. runnable validation evidence
4. a response to review findings
5. consensus before closure
6. archived reasoning

## Why The Oracle Matters

Current trust is anchored by:

- `rt.run_cpu(...)` as the native C/C++ oracle

Then backend validation compares that oracle against:

- `rt.run_embree(...)`
- `rt.run_optix(...)`

When an external checker is part of the goal, the current repo also treats
indexed PostGIS queries on the Linux host as an additional ground-truth check
for accepted bounded real-data packages.

That is the main correctness pattern in the current repo.

## Expected Goal Loop

1. define the goal
2. review the scope
3. implement within that scope
4. run validation
5. get external review
6. revise if needed
7. archive and close after consensus

## What Counts As Validation

Depending on the goal, validation may include:

- unit tests
- integration tests
- authored examples
- oracle/backend parity checks
- benchmark harnesses
- generated reports

## Canonical Test Matrix

The live repo now distinguishes three test layers:

- unit:
  - language, lowering, reference behavior, regression checks, report smoke
- integration:
  - backend wiring, runtime interop, backend-specific acceptance slices that are
    still narrower than full package closure
- system:
  - accepted bounded-package checks and larger end-to-end workflow slices

The canonical runner is:

- `python scripts/run_test_matrix.py --group unit`
- `python scripts/run_test_matrix.py --group integration`
- `python scripts/run_test_matrix.py --group system`
- `python scripts/run_test_matrix.py --group full`
- `python scripts/run_test_matrix.py --group v3_current`
- `python scripts/run_test_matrix.py --group v4_prep`

Use `python3` instead if that is what your shell exposes.

`v3_current` is the current V3 closure suite. It intentionally runs only the
explicit V3 current modules starting at Goal4508 because the default unittest
discovery pattern does not include every `goal*_test.py` file and because V4
preparatory embedding/C ABI/zero-copy work must not define V3 completion.

`v4_prep` is the separate audit group for archived V4 preparatory material. It
keeps C ABI, embedding, SDK-staging, binding, and zero-copy prep evidence
checkable without turning it into the V3 current validation surface.

The full discovery command remains useful:

- `python -m unittest discover -s tests -p '*test.py'`

But the test-matrix runner is the clearer release-style verification surface.
`make test` follows `v3_current`; use `make test-all` for the full discovery
sweep.

## What Consensus Means

Consensus does not mean every reviewer must use identical wording.

It means:

- the blocking issues are resolved or honestly scoped
- the accepted result is technically trustworthy enough to move forward
- the archived outcome states the remaining risks clearly

## Boundary

This document is the live process summary.

The stricter audit contract for turning review into accepted repo state is in:

- `docs/audit_flow.md`

Detailed historical execution of that process lives in:

- `history/`
- accepted per-goal reports
