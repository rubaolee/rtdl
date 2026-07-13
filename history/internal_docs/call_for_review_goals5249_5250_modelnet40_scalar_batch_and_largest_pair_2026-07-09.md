# Call For Review - Goals5249-5250 ModelNet40 Scalar Route Batch And Largest Pair

Please strictly review Goals5249-5250:

```text
history/internal_docs/goal5249_modelnet40_scalar_batch10_route_result_2026-07-09.md
history/internal_docs/goal5250_modelnet40_largest_pair_scalar_route_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5249_modelnet40_scalar_batch10_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5249_modelnet40_scalar_batch10_artifacts_2026-07-09.tar.gz
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_artifacts_2026-07-09.tar.gz
```

## Context

Goal5248 showed the current scalar route on one large ModelNet40 airplane pair.
Goals5249-5250 make the evidence stronger in two different ways:

```text
Goal5249: 10 selected ModelNet40 categories, 10/10 matched
Goal5250: largest selected ModelNet40 unique pair, 1/1 matched
```

Both use the current scalar route:

```text
native_cuda grid-cell builder
native_cuda local-grid seed
inline frontier nearest
global-bound early break
author-float32 normalization
directed-a-to-b comparison
author-only validation
```

## Review Questions

1. Does Goal5249 truly prove the batch harness now uses the current scalar
   route switches, especially `--grid-cell-builder native_cuda` and
   `--global-bound-early-break`?
2. Does Goal5249 support "10 selected ModelNet40 categories matched", while
   avoiding a false "all ModelNet40 scalar route coverage" claim?
3. Does Goal5250 correctly identify and test the largest selected unique pair?
4. Are the author-only validation boundaries acceptable and clearly stated?
5. Do both reports preserve the caveat:

```text
per_source_witness_exact = false
```

6. Are performance numbers denominator-explicit, with no speedup/parity claim?
7. Is it fair to say these goals strengthen ModelNet40 scalar route evidence,
   but still do not close full X-HD paper reproduction?
8. Are the claim boundaries complete, especially forbidding:

```text
full paper reproduction
all ModelNet40 scalar coverage
exact per-source witnesses
exact paper byte-input identity
Figure reproduction
author internal AvgTime parity
```

## Expected Answer Shape

```text
Verdict:
  approve_goals5249_5250...
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
