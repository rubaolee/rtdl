# Call For Review - Goal5254 ModelNet40 Route-Label Performance Matrix

Please strictly review Goal5254:

```text
history/internal_docs/goal5254_modelnet40_route_label_performance_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5254_modelnet40_route_label_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/summarize_modelnet40_route_matrix.py
```

## Context

We now have two ModelNet40 all-400 RTDL routes:

```text
Goal5252 fast scalar route:
  400 / 400 matched
  per_source_witness_exact = false
  route_wall_sec sum = 145.7630s

Goal5253 exact-witness route:
  400 / 400 matched
  per_source_witness_exact = true for 400 / 400
  route_wall_sec sum = 424.5629s
```

Goal5254 generates a denominator-explicit matrix over the same 400 cases.

## Review Questions

1. Does the matrix correctly require identical case sets between Goal5252 and
   Goal5253?
2. Are the two route labels correctly separated?
3. Are author process wall and author internal `Running.AvgTime` kept as
   distinct denominators?
4. Are the ratios reported honestly, without parity/speedup overclaim?
5. Does the report correctly state that the fast scalar route is not an exact
   witness route?
6. Does the report correctly state that the exact-witness route is slower but
   functionally stronger?
7. Is the tent scalar outlier correctly identified as a fallback-tail issue?
8. Is the matrix script app-owned and free of RTDL core changes?
9. Should future X-HD performance summaries be required to name the route label?
10. Are any amendments required before this matrix becomes the current
    ModelNet40 performance reference?

## Expected Answer Shape

```text
Verdict:
  approve_goal5254...
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
