# Call For Review: Goal5096 RT-DBSCAN Bounded Same-Input Closeout

Please review the consolidated RT-DBSCAN bounded same-input packet:

```text
history/internal_docs/goal5096_rt_dbscan_bounded_same_input_closeout_2026-07-07.md
history/internal_docs/rt_dbscan_review_opinions_register_2026-07-07.md
history/internal_docs/goal5093_rt_dbscan_authorofficial_core_count_pod_execution_attempt_2026-07-07.md
history/internal_docs/goal5094_rt_dbscan_authorofficial_component_signature_gate_2026-07-07.md
history/internal_docs/goal5095_rt_dbscan_border_noise_component_signature_gate_2026-07-07.md
history/internal_docs/goal5095_review_amendment_response_2026-07-07.md
history/internal_docs/review_goal5095_amended_component_partition_gate_verified_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_core_count_gate.py
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
tests/goal5092_rt_dbscan_authorofficial_gate_packet_test.py
tests/goal5094_rt_dbscan_authorofficial_component_signature_gate_test.py
```

## Review Questions

1. Does Goal5096 correctly close only bounded same-input RT-DBSCAN gates, not
   full RT-DBSCAN paper reproduction?
2. Does the Goal5093 core-count evidence show exact AuthorOfficial-vs-RTDL
   equality (`core_count=7`, `matched=true`) on the tiny fixture?
3. Does the amended component gate compare canonical point partitions modulo
   label renaming, rather than only sorted component-size signatures?
4. Do the tiny and border/noise POD summaries both show:
   `schema=...component_partition_gate.v2`, `signature_matched=true`,
   `component_partition_matched=true`, `core_flags_matched=true`, and
   `matched=true`?
5. Does the border/noise fixture actually verify a non-core border point and a
   noise point at the point-partition level?
6. Does the regression test prove the old signature-only gate would miss a
   border swap that the new partition gate catches?
7. Does the RTDL route remain generic fixed-radius graph infrastructure:
   count-threshold and OptiX+Numba component-label routes, with no
   RT-DBSCAN-specific core primitive?
8. Do the README, manifest, and results README avoid stale `not_started`,
   `pod_ready_not_executed`, and signature-only wording?
9. Does the packet avoid claims of exact author label-ID parity, full DBSCAN
   output-format parity, exact paper dataset reproduction, performance, speedup,
   or author parity?
10. Is the register state accurate: Goal5095 externally verified, Goal5094
    signature-only claim superseded/strengthened by the amended partition gate,
    and consolidated Goal5096 still pending review?

## Expected Verdict Labels

Approve if valid:

```text
approve_goal5096_rt_dbscan_bounded_same_input_closeout
```

Require amendments if needed:

```text
revise_goal5096_rt_dbscan_bounded_same_input_closeout
```
