# Call For Review: Goal5095 RT-DBSCAN Border/Noise Component-Partition Gate

Please review:

```text
history/internal_docs/goal5095_rt_dbscan_border_noise_component_signature_gate_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/border_noise3d_component_signature.csv
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
Paper-reproduction-apps/rt-dbscan-paper/results/component_signature_border_noise_local_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
tests/goal5094_rt_dbscan_authorofficial_component_signature_gate_test.py
```

## Review Questions

1. Does the second fixture actually include a border point and a noise point?
2. Is the border point ordering justified by the author's `xID > primID` call-2
   condition?
3. Does the POD summary show exact normalized signature equality:
   `core_count=10`, `component_sizes=[5,6]`, `noise_count=1`?
4. Does the POD summary also show canonical point-partition equality:
   `component_partition_matched=true`, `core_flags_matched=true`, and
   `matched=true`?
5. Does the amended comparator correctly avoid exact author label-ID dependence
   while still detecting border swaps that a sorted component-size signature
   would miss?
6. Does the RTDL route remain generic:
   `generic_prepared_optix_numba_grouped_stream_component_labels_3d`?
7. Does the report avoid claiming full DBSCAN output-format parity, exact paper input
   reproduction, or performance?
8. Are the tests sufficient to protect the border/noise fixture semantics,
   including the regression that proves signature-only equality misses a border
   swap?
9. Should Goals5093-5095 now be sent as a consolidated RT-DBSCAN bounded-line
   review packet?

## Expected Verdict Labels

Approve if valid:

```text
approve_goal5095_rt_dbscan_border_noise_component_partition_gate
```

Require amendments if needed:

```text
revise_goal5095_rt_dbscan_border_noise_gate
```
