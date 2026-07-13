# Call For Review - Goal5260 X-HD hd_exec-Compatible All-400 ModelNet40 Batch

Please strictly review Goal5260.

## Files Under Review

```text
history/internal_docs/goal5260_xhd_hd_exec_all400_modelnet40_batch_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
tests/goal5260_xhd_hd_exec_all400_batch_artifact_test.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Prerequisite context:

```text
history/internal_docs/goal5253_modelnet40_all400_exact_seed_witness_route_result_2026-07-09.md
history/internal_docs/call_for_review_goals5255_5259_xhd_hd_exec_user_entrypoint_batch_consolidated_2026-07-09.md
```

## Questions

1. Does Goal5260 prove that the hd_exec-compatible batch bridge, not only the
   older batch harness, can run all 400 public ModelNet40 unique pair identities?

2. Are all 400 cases actually matched against author rerun HDResult within
   tolerance?

3. Is the route label `cell-mbr-exact-witness` correctly carried through every
   case?

4. Does the artifact prove `per_source_witness_exact=true` for every case?

5. Does the report correctly preserve the boundary:

```text
public ModelNet40 rerun contract != exact paper byte-input identity
all-400 ModelNet40 != all X-HD paper datasets/Figures
RTDL route wall time != author internal Running.AvgTime
```

6. Are timing summaries useful but safely denominator-labeled?

7. Should this goal supersede Goal5259 first-3 as the user-entrypoint batch
   bridge evidence, while Goals5252-5254 remain historical/bulk route evidence?

8. Does anything in Goal5260 overclaim author RT-core algorithm equivalence or
   performance parity?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | revise | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
...
8. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goal5260_xhd_hd_exec_all400_modelnet40_batch_bridge
```
