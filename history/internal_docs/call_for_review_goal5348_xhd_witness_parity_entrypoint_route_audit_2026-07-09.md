# Call For Review - Goal5348 X-HD Witness Parity / Entrypoint Route Audit

Please strictly review Goal5348.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5348_witness_parity_entrypoint_route_audit.json
tests/goal5348_xhd_witness_parity_entrypoint_audit_test.py
history/internal_docs/goal5348_xhd_witness_parity_entrypoint_route_audit_result_2026-07-09.md
```

Primary supporting evidence:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5347_functional_feature_parity_matrix.json
```

## Review Questions

1. Does `run_xhd_rtdl_hd_exec.py` actually default `auto + n_dims=3 + execution=gpu`
   to `cell-mbr-exact-witness` rather than `cell-mbr-fast-scalar`?
2. Do the ModelNet40 all-400 and four Stanford representative artifacts really
   show `route_label=cell-mbr-exact-witness` and `per_source_witness_exact=true`?
3. Does the fast-scalar Goal5212 artifact really show an exact scalar match but
   `per_source_witness_exact=false` with many early-aborted sources?
4. Is Goal5348's refinement of Goal5347 correct: exact-witness is no longer a
   broad blocker for the user-facing reviewed entrypoint, but fast-scalar remains
   exact-value-only?
5. Does the Goal5348 test suite cover the important distinction between
   exact-witness entrypoint evidence and fast-scalar performance-route evidence?
6. Does the report avoid claiming full paper reproduction, exact input identity,
   author RT-core algorithm identity, performance parity, or fast-scalar witness
   exactness?
7. Is it acceptable to update the functional parity matrix wording after this
   review to split witness status into exact-witness entrypoint coverage versus
   fast-scalar witness limitation?

## Requested Verdict Shape

Please answer with:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions 1-7:
Requested verdict label:
```

Suggested label if approved:

```text
approve_goal5348_witness_parity_entrypoint_route_audit
```
