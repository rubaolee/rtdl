# Call For Review: Goal5075 RT-BarnesHut Generic Aggregate Force-Output Bridge

Date: 2026-07-06

## Requested Verdict Label

`approve_goal5075_app_owned_scalar_force_output_bridge`

## Review Scope

Please review:

- `history/internal_docs/goal5075_rt_barneshut_generic_aggregate_force_output_bridge_result_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

## Context

Goals5063-5074 were approved as a generic aggregate-hierarchy rearchitecture for RT-BarnesHut. The approved next step was an app-owned bounded force-output bridge.

Goal5075 implements that bridge. It maps generic aggregate reducer rows into the RT-BarnesHut app's scalar force-output rows, while keeping RTDL core app-neutral.

## Review Questions

1. Does the implementation correctly recognize that the app force output is scalar, not a 3D vector?
2. Is the `0.1` force scale kept in the app adapter rather than promoted into RTDL core?
3. Does the bridge use public generic RTDL aggregate-hierarchy APIs rather than a torch extension, native OptiX hook, or author payload shortcut?
4. Does the implementation preserve the boundary that RTDL core produces generic reducer rows and the RT-BarnesHut app owns scalar force formatting?
5. Do the tests prove that optional Numba output and CPU reference output map to identical scalar force rows on the controlled route?
6. Does the CLI smoke evidence show that the app can write a bounded scalar force file from prepared arrays?
7. Are the claim boundaries correct: not author binary comparator, not paper completion, not performance, not device-resident/native?
8. Do the leak checks sufficiently show that no BarnesHut or RayJoin identity was inserted into `src/rtdsl/aggregate_hierarchy.py`?
9. Is it acceptable that force-file text formatting uses finite decimal output with file-level tolerance, while internal bridge comparison remains exact on the in-memory rows?
10. Should the next goal be a bounded same-input scalar force comparator against an author prepared-state plus force dump, still owned by the paper app?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 10 review questions
