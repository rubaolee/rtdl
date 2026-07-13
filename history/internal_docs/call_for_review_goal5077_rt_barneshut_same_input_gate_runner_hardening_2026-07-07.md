# Call For Review: Goal5077 RT-BarnesHut Same-Input Gate Runner Hardening

Date: 2026-07-07

## Requested Verdict Label

`approve_goal5077_cross_platform_same_input_force_gate_runner`

## Review Scope

Please review:

- `history/internal_docs/goal5077_rt_barneshut_same_input_gate_runner_hardening_result_2026-07-07.md`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.sh`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

## Context

Goal5076 added a same-input scalar force comparator mode. Goal5077 makes the surrounding gate easier to run across environments by adding a Python runner and keeping the shell script as a thin wrapper.

## Review Questions

1. Does the Python runner correctly wrap `aggregate-numba-force-compare` rather than reimplementing comparison logic?
2. Does the runner accept explicit prepared arrays and expected force files, making it usable for both local synthetic artifacts and POD patched-author artifacts?
3. Does it fail closed when required inputs are missing?
4. Does the shell runner remain a thin wrapper around the Python runner?
5. Do the tests cover successful synthetic execution and missing-input failure?
6. Does the goal avoid claiming patched-author binary parity when the local run used synthetic author-contract reference artifacts?
7. Does the goal avoid performance, native/backend, and full paper-reproduction claims?
8. Does the core scan support that no app-specific logic entered `src/rtdsl/aggregate_hierarchy.py`?
9. Is the next recommended goal correctly identified as POD execution against patched-author same-input artifacts?
10. Are review opinions from Goal5075 preserved and not contradicted?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 10 review questions
