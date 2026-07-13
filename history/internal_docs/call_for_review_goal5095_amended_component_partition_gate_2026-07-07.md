# Call For Review: Goal5095 Amended RT-DBSCAN Component-Partition Gate

Please review the Goal5095 amendment response:

```text
history/internal_docs/goal5095_review_amendment_response_2026-07-07.md
history/internal_docs/goal5095_rt_dbscan_border_noise_component_signature_gate_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
tests/goal5094_rt_dbscan_authorofficial_component_signature_gate_test.py
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/component_signature_gate_local_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/component_signature_border_noise_local_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
```

## Prior Blocking Finding

The prior review correctly found that the old Goal5095 comparator was
signature-only:

```text
{core_count, sorted(component_sizes), noise_count}
```

That was blind to a border point being assigned to the wrong component when the
sorted component-size multiset stayed the same.

## Review Questions

1. Does the runner now use the generic label-producing RTDL route
   `radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns`
   rather than the signature-only route?
2. Does the summary now include and require:
   `signature_matched=true`, `component_partition_matched=true`,
   `core_flags_matched=true`, and `matched=true`?
3. Does canonical point-partition comparison avoid exact author label-ID
   dependence while detecting the border-swap failure mode from the prior
   review?
4. Do the tiny and border/noise POD summaries both use schema
   `rtdl.paper_reproduction.rt_dbscan.authorofficial_component_partition_gate.v2`
   and pass AuthorOfficial-vs-RTDL comparison?
5. Does the regression test
   `test_canonical_partition_detects_border_swap_that_signature_misses` prove
   the old signature-only comparator would have missed the reviewed failure?
6. Do the report, README, and manifest remove the old "covers border assignment
   at signature level" overclaim?
7. Does the RTDL route remain generic and avoid adding an RT-DBSCAN-specific
   core primitive?
8. Does the amended packet still avoid full paper reproduction, exact label-ID
   parity, exact paper dataset, output-format, performance, and speedup claims?

## Expected Verdict Label

Approve if valid:

```text
approve_goal5095_amended_component_partition_gate
```

Require amendments if needed:

```text
revise_goal5095_amended_component_partition_gate
```
