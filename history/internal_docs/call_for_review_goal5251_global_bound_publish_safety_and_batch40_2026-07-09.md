# Call For Review - Goal5251 Global-Bound Publish Safety And ModelNet40 Batch40

Please strictly review Goal5251:

```text
history/internal_docs/goal5251_global_bound_publish_safety_and_modelnet40_batch40_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_chair_global_bound_fixed_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_modelnet40_scalar_batch40_fixed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_modelnet40_scalar_batch40_fixed_artifacts_2026-07-09.tar.gz
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_fixed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_fixed_artifacts_2026-07-09.tar.gz
```

## Context

Goal5251 found and fixed a correctness bug in the generic global-bound
early-break route. The pre-fix ModelNet40 batch40 run matched 39/40 and failed:

```text
chair_0162.off -> chair_0131.off
pre-fix global-bound abs diff = 0.0009493921217607892
```

The same pair without global-bound matched. The native fix marks deferred
frontier rows with `optixSetPayload_6(2u)`, preventing their upper bounds from
being published as global exact scalar bounds.

After rebuild:

```text
chair fixed global-bound matched
batch40 fixed matched 40/40
largest selected ModelNet40 pair fixed matched 1/1
```

## Review Questions

1. Is the root-cause analysis correct: global-bound publication was unsafe when
   the query had deferred frontier rows?
2. Is the native fix sufficiently generic and app-neutral?
3. Does the `optixSetPayload_6(2u)` marker actually prevent unsafe publication,
   given the existing `p6 == 0` publish guard?
4. Does the fixed chair evidence prove the failure was repaired?
5. Does the fixed batch40 evidence support 40 selected ModelNet40 categories
   matched, while avoiding all-400 claims?
6. Does the fixed largest-pair evidence remain valid after the native fix?
7. Are performance numbers denominator-explicit and not used as parity claims?
8. Does the report preserve the caveat:

```text
per_source_witness_exact = false
```

9. Should Goal5251 supersede the pre-fix Goal5249/5250 current-route evidence?
10. Are any additional tests required beyond the source guard and POD
    correctness evidence?

## Expected Answer Shape

```text
Verdict:
  approve_goal5251...
  or approve_with_required_amendments
  or block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Question answers:
  1. ...
  ...
```
