# Call For Review: Goal5312 X-HD WaterBodies -> BlockGroups Full-Public RTDL Route

Please strictly review Goal5312.

Primary result:

```text
history/internal_docs/goal5312_xhd_water_bg_full_public_rtdl_route_result_2026-07-09.md
```

Implementation / artifacts:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_2d_zero_z_cell_mbr_pod_smoke.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_cell_mbr.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_exact_witness.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_summary.json
tests/goal5312_xhd_2d_zero_z_cell_mbr_route_test.py
tests/goal5312_xhd_2d_zero_z_cell_mbr_pod_artifact_test.py
tests/goal5312_xhd_water_bg_full_public_rtdl_summary_test.py
```

Context:

Goal5311 ran the author `hd_exec` on the same full-public WaterBodies ->
BlockGroups WKT candidate:

```text
author same-public HDResult = 0.8970130085945129
paper-log HDResult = 0.8964367508888245
```

Goal5312 adds:

```text
explicit 2-D -> 3-D zero-z lift for cell-MBR route
streaming WKT matrix front door
full-public RTDL fast-scalar run
full-public RTDL exact-witness-label run
```

Critical result:

```text
RTDL fast-scalar HDResult = 0.8964380566690101
RTDL exact-witness-label HDResult = 0.8964380566690101
abs diff vs author same-public = 0.0005749519255028313
abs diff vs paper log = 0.000001305780185645311
```

Requested verdict labels:

```text
approve_goal5312_full_public_rtdl_execution_but_author_mismatch_carried_forward
revise_goal5312_due_to_overclaim_or_missing_evidence
block_goal5312_due_to_invalid_route_or_claim_boundary
```

Review questions:

1. Does Goal5312 actually add a fail-closed explicit 2-D -> 3-D zero-z lift,
   rather than silently routing all 2-D inputs through 3-D cell-MBR?

2. Is the lift generic and app-neutral enough, or does it smuggle X-HD /
   Figure-5 semantics into RTDL core?

3. Does the streaming WKT matrix loader preserve the prior app-owned WKT
   contract, especially outer-ring-only polygon semantics?

4. Do the local tests sufficiently cover the lift helper, fail-closed 2-D
   route behavior, streaming WKT matrix equivalence, and hd_exec wrapper
   fail-closed behavior?

5. Does the POD smoke prove the explicit 2-D lift can reach the OptiX
   cell-MBR route on CUDA hardware?

6. Do the full-public RTDL artifacts prove route execution on the same
   WaterBodies-BlockGroups candidate and the same point counts as Goal5311?

7. Is the report correct to say the full-public RTDL execution passed but the
   author same-public scalar match failed?

8. Is the report correct to reject the fast-scalar route as a correctness gate
   because it uses global-bound early break and has non-exact per-source
   witnesses?

9. Is the report cautious enough about the `cell-mbr-exact-witness` result?
   It has `per_source_witness_exact=true` metadata but still does not match the
   same-public author HDResult. Should that route label / metadata be treated
   as suspect for this 2-D lifted WKT case until Goal5313 explains it?

10. Does the report properly prevent the tempting but invalid claim that RTDL
    "matches the paper log" for Figure 5, given that the same public input's
    author rerun does not match the paper log?

11. Does Goal5312 correctly refuse exact paper dataset recovery, Figure-5
    reproduction, author RT-core equivalence, and performance ratio claims?

12. Is Goal5313 correctly identified as semantic-mismatch investigation before
    any performance matrix or broader claim?

Expected answer shape:

```text
Verdict: <one requested verdict label or stricter>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
12. ...
```
