# Call For Review - Goal5248 ModelNet40 Second Level-B Scalar Route

Please strictly review Goal5248:

```text
history/internal_docs/goal5248_modelnet40_second_level_b_scalar_route_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5248_modelnet40_airplane_scalar_route_repeat1_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5248_modelnet40_airplane_scalar_route_repeat2_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5248_modelnet40_airplane_scalar_route_repeat3_2026-07-09.json
```

## Review Context

Goal5248 runs the current Goal5247 scalar `HDResult` route on a second large
Level-B public X-HD workload:

```text
ModelNet40 airplane_0036.off -> airplane_0515.off
```

This pair has prior ModelNet40 provenance and author output from Goals5229-5231.
Goal5248 does not rerun all 400 ModelNet40 pairs. It selects one large public
pair and checks whether the current scalar route generalizes beyond the
Dragon -> scaled AsianDragon graphics workload.

## Things To Attack

Please be especially strict on:

1. Does the evidence really support "second Level-B public workload family", or
   is that wording too broad?
2. Is the `author-only` validation boundary acceptable for this large pair,
   given that exact all-pairs reference is not run?
3. Does the report correctly preserve the critical caveat:

```text
per_source_witness_exact = false
```

4. Are the performance comparisons framed only as diagnostics, with no
   author-parity or paper-performance claim?
5. Is it correct to compare against the prior Goal5229 exact normalized route
   for the same pair as a diagnostic, or should that be further limited?
6. Does the result accidentally imply all ModelNet40 cases were run through the
   scalar route? If so, require correction.
7. Does this close the prior "single workload only" critique enough to say
   "two workload families", or should it remain "two selected public workloads"?
8. Are the forbidden summaries complete:

```text
full paper reproduction
all ModelNet40 scalar route coverage
exact per-source witnesses
exact paper byte-input identity
Figure 5-11 reproduction
author internal Running.AvgTime parity
speedup/parity claim
```

## Expected Answer Shape

Please answer with:

```text
Verdict:
  approve_goal5248...
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
  2. ...
  ...
```
