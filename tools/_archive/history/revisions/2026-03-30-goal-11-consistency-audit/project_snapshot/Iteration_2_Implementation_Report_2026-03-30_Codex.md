# Iteration 2 Implementation Report (2026-03-30, Codex)

## Revision Summary

This revision addressed the consistency issues found in the independent Codex
review without adding any new workload features.

Changes made:

- made `make build` compiler-only so it no longer depends on Embree
- clarified `README.md` so build/test behavior is accurate for fresh checkouts
- updated language-facing docs in `docs/rtdl/` to describe the current six-workload surface
- updated the plan schema to accept the Goal 10 workload kinds and predicates
- updated language regression tests to cover:
  - `ray_tri_hitcount`
  - `segment_polygon_hitcount`
  - `point_nearest_segment`
- made Embree-dependent tests skip automatically when Embree is unavailable

## Files Revised

- `Makefile`
- `README.md`
- `docs/rtdl/README.md`
- `docs/rtdl/dsl_reference.md`
- `docs/rtdl/programming_guide.md`
- `docs/rtdl/llm_authoring_guide.md`
- `schemas/rayjoin_plan.schema.json`
- `tests/_embree_support.py`
- `tests/rtdsl_embree_test.py`
- `tests/goal10_workloads_test.py`
- `tests/baseline_integration_test.py`
- `tests/evaluation_test.py`
- `tests/rtdsl_language_test.py`

## Verification

Re-run after revision:

- `make build`
- `python3 -m unittest discover -s tests -p '*_test.py'`
- `PYTHONPATH=src:. python3 apps/rtdsl_python_demo.py`

All passed on the revised snapshot.
