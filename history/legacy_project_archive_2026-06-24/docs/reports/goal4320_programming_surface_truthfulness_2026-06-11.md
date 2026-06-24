# Goal4320: Programming Surface Truthfulness

Date: 2026-06-11

## Verdict

`accept-with-boundary` for a Fable5 F2 programming surface truthfulness
follow-up.

The whole-project review correctly warned that learner docs can make the
small `@rt.kernel` teaching DSL look like the entire high-performance path,
while current promoted benchmark routes often use primitive discovery,
prepared front doors, and explicit partner continuation directly. Goal4320
makes that distinction explicit in current learner-facing docs.

## What Changed

- Added `docs/learn/programming_surfaces.md`, naming the three current
  programming surfaces:
  - kernel DSL for the generic authoring and teaching shape;
  - primitive/prepared front doors for promoted generic performance contracts;
  - CuPy/Numba partner continuation for explicit typed-column custom logic.
- Updated `README.md` so the core idea is a generic RTDL contract, not only an
  `@rt.kernel` function.
- Linked the new page from `docs/README.md`, `docs/learn/README.md`,
  `tutorials/current/README.md`, and `docs/rtdl/programming_guide.md`.
- Updated `tutorials/current/02_kernel_shape_and_backends.md` to state that
  the kernel shape is the mental model, not the only performance entry point.
- Added `tests/goal4320_programming_surface_truthfulness_test.py`.

## Boundary

Goal4320 does not authorize any new public claim surface.

Goal4320 does not implement a new lowering bridge from arbitrary `@rt.kernel`
programs to every prepared high-performance route. It does not move benchmark
apps, change runtime behavior, authorize a release, authorize public speedup
wording, authorize broad RT-core wording, authorize package-install wording,
authorize automatic partner selection, or authorize true-zero-copy wording.

This is a truthfulness and learner-clarity step: if the project later wants the
kernel DSL itself to become the main performance route, that requires a separate
engineering goal with runtime parity and timing evidence.

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4320_programming_surface_truthfulness_test tests.goal4248_current_public_docs_claim_boundary_scan_test
```

Observed result: 10 tests passed. The public-doc claim scan also passed with
35 scanned files and zero hard blockers.
