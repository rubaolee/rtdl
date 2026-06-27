# Goal 328 Report: v0.5 Layout Types Collision Fix

Date:
- `2026-04-12`

Goal:
- remove the `rtdsl.types` stdlib-collision risk identified by the full Gemini
  repo audit

Files changed:
- `src/rtdsl/layout_types.py`
- `src/rtdsl/api.py`
- `src/rtdsl/ir.py`
- `src/rtdsl/__init__.py`
- `tests/test_core_quality.py`
- `tests/goal328_v0_5_layout_types_name_collision_test.py`

What changed:
- the old internal module `src/rtdsl/types.py` was renamed to
  `src/rtdsl/layout_types.py`
- internal imports now target `layout_types`
- the package-level public `rtdsl` exports remain intact through
  `src/rtdsl/__init__.py`
- a focused regression test now checks both:
  - stdlib `types` wins even if `src/rtdsl` is inserted into `sys.path`
  - the public `rtdsl` layout/type surface still imports correctly

Why this matters:
- the whole-repo Gemini audit correctly identified `types.py` as a namespace
  risk
- this kind of collision is a packaging/integration hazard, not just a style
  nit
- the fix is small, bounded, and appropriate for the current preview line

Honesty boundary:
- this is a naming and packaging hardening fix
- it does not change workload semantics or backend behavior
