# Call For Review: Goal5076 RT-BarnesHut Same-Input Scalar Force Comparator Gate

Date: 2026-07-06

## Requested Verdict Label

`approve_goal5076_app_owned_same_input_scalar_force_comparator_gate`

## Review Scope

Please review:

- `history/internal_docs/goal5076_rt_barneshut_same_input_scalar_force_comparator_gate_result_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.sh`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

## Context

Goal5075 was approved as an app-owned scalar force-output bridge. Goal5076 adds a bounded comparator gate around that bridge.

The gate accepts:

- prepared aggregate arrays,
- an expected scalar force file,
- tolerance settings.

It emits:

- candidate scalar force rows from the generic RTDL aggregate-hierarchy route,
- a force-file comparison summary,
- a bounded same-input comparator status.

## Review Questions

1. Does the new `aggregate-numba-force-compare` CLI mode correctly compose the Goal5075 bridge with the app-owned force comparator?
2. Does the shell runner use existing patched-author same-input artifacts as inputs, without rebuilding comparison logic in RTDL core?
3. Does the implementation preserve the app/system boundary: generic aggregate traversal in RTDL, scalar force comparator and force formatting in the paper app?
4. Does the local synthetic smoke prove the gate works without requiring CUDA/POD availability?
5. Are claim boundaries correct: not full paper reproduction, not performance, not native/device-resident, not author binary proof for the local synthetic smoke?
6. Is it acceptable that `same_input_author_comparator` becomes true only for this bounded scalar force-file comparator, while `paper_reproduction_complete` remains false?
7. Does the runner provide enough POD-ready structure for a later patched-author artifact validation goal?
8. Do the tests sufficiently protect the CLI wiring and comparator success path?
9. Do the compile and core identity scans support that no app-specific comparator logic entered `src/rtdsl/aggregate_hierarchy.py`?
10. Should the next goal be a POD execution of this gate against patched-author same-input prepared arrays and force dumps?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 10 review questions
