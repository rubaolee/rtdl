# Call For Review - Goals5318-5349 X-HD Readiness, Functional Parity, Witness, And Variant Packet

Please strictly review the current X-HD state packet through Goal5349.

This packet supersedes the earlier Goal5348 packet by adding the hd_exec variant
value-surface change.

## Scope

```text
Goals5318-5344: external provenance / mapped-candidate / POD plan and dry-run runner infrastructure
Goal5345: exact reproduction readiness gate
Goal5346: external artifact surface refresh
Goal5347: functional feature parity matrix
Goal5348: witness parity / hd_exec entrypoint route audit
Goal5349: hd_exec variant value-surface support
```

## Primary Files

```text
history/internal_docs/goal5345_xhd_exact_reproduction_readiness_gate_result_2026-07-09.md
history/internal_docs/goal5346_xhd_external_artifact_surface_refresh_result_2026-07-09.md
history/internal_docs/goal5347_xhd_functional_feature_parity_matrix_result_2026-07-09.md
history/internal_docs/goal5348_xhd_witness_parity_entrypoint_route_audit_result_2026-07-09.md
history/internal_docs/goal5349_xhd_hd_exec_variant_value_surface_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5345_exact_reproduction_readiness.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5346_external_artifact_surface_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5347_functional_feature_parity_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5348_witness_parity_entrypoint_route_audit.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5349_hd_exec_variant_value_surface.json

Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/README.md
tests/goal5348_xhd_witness_parity_entrypoint_audit_test.py
tests/goal5349_xhd_hd_exec_variant_value_surface_test.py
```

## Key Claims To Review

### Exact Reproduction Readiness

Goal5345 says:

```text
pod_execution_allowed_now = false
classification = exact_reproduction_not_pod_ready__await_artifact_access
```

Goal5346 says:

```text
new_exact_input_artifact_found = false
exact_input_blocker_removed = false
ACM supplement still returns 403 / HTML / no zip magic
GitHub has source/scripts/logs but no release/data/HDDatasets artifact
```

Please verify that POD exact-reproduction execution remains correctly blocked.

### Functional Parity Matrix

Goal5347 says:

```text
full_functional_parity_ready = false
highest_current_reproduction_level = Level-B same-source representative and bounded same-input values
```

Please verify that the matrix is honest and that Goals5348-5349 refine it rather
than upgrading it to full parity.

### Witness Route Refinement

Goal5348 says:

```text
auto + n_dims=3 + execution=gpu -> cell-mbr-exact-witness
ModelNet40 all-400 and four Stanford representative hd_exec artifacts have per_source_witness_exact=true
Goal5212 fast-scalar route matches scalar HDResult but has per_source_witness_exact=false
```

Please verify the distinction:

```text
covered: hd_exec-compatible exact-witness route on reviewed Level-B artifacts
not covered: fast-scalar exact per-source witnesses
not covered: author RT-core algorithm identity
not covered: exact paper dataset reproduction
```

### Variant Value Surface

Goal5349 says:

```text
The RTDL hd_exec-compatible runner now accepts -variant eb|nn|itk|clover|rt.
Every variant returns a directed input1->input2 HDResult via the selected RTDL route.
Non-rt variants are value-compatible only; author variant-specific algorithms and
performance denominators are not reproduced.
```

Please verify that this improves option-surface compatibility without creating
an author-algorithm or Figure 5 baseline claim.

## Tests Reported

```text
py -m unittest tests.goal5345_xhd_exact_reproduction_readiness_test tests.goal5346_xhd_external_artifact_surface_refresh_test tests.goal5347_xhd_functional_feature_parity_matrix_test tests.goal5348_xhd_witness_parity_entrypoint_audit_test tests.goal5349_xhd_hd_exec_variant_value_surface_test
Ran 21 tests OK

py -m unittest tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test tests.goal5349_xhd_hd_exec_variant_value_surface_test
Ran 9 tests OK
```

## Forbidden Conclusions

Please mark as blocking if any reviewed document implies:

```text
full X-HD paper reproduction is complete;
exact paper dataset identity is proved;
Figure 5-11 reproduction is complete;
author-vs-RTDL performance ratio is authorized;
POD execution should run before Goal5345 pod_execution_allowed_now=true;
fast-scalar early-break route has exact per-source witnesses;
exact-witness route proves author RT-core algorithm identity;
non-rt variants reproduce author eb/nn/itk/clover algorithms or performance.
```

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to key review questions:
Requested verdict label:
```

Suggested label if approved:

```text
approve_goals5318_5349_xhd_readiness_functional_witness_and_variant_packet
```
