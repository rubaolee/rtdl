# Call For Review: Goal5225 ModelNet40 Heavy-Pair Feasibility

Date: 2026-07-09

Please strictly review Goal5225:

```text
history/internal_docs/goal5225_modelnet40_heavy_pair_feasibility_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5225_modelnet40_algorithm_aware_largest1_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5225_modelnet40_algorithm_aware_largest10_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5225_modelnet40_heavy_pair_feasibility_artifacts_2026-07-09.tar.gz
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
```

## Context

Goal5224 proved a 40-category representative ModelNet40 batch. Goal5225 probes
the heaviest unique pairs before attempting all 400 unique pairs.

The all-unique set has 400 pairs and includes multi-million-point inputs:

```text
max total points = 2,726,286
```

## Review Questions

1. Does the static workload analysis correctly show 400 unique ModelNet40 pairs
   across 40 categories and a max pair size of 2,726,286 points?
2. Does the runner's new selection strategy remain app-owned and avoid adding
   ModelNet40/X-HD semantics to RTDL core?
3. Does the largest-1 probe match author/paper and RTDL within tolerance?
4. Does the largest-10 probe show 10/10 matched on the heaviest unique pairs?
5. Are the reported route/full-total timings framed as feasibility data rather
   than a performance ratio?
6. Is the conclusion correct that all-400 is plausible but should be run with
   chunking/resume/failure-capture controls?
7. Does the report avoid claiming all ModelNet40, exact byte identity, author
   parity, or full X-HD reproduction?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
7. ...
```

Requested verdict label if approved:

```text
approve_goal5225_modelnet40_heavy_pair_feasibility
```
