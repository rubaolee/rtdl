# Goal5095 RT-DBSCAN Border/Noise Component-Partition Gate

Date: 2026-07-07

## Verdict

`completed_rt_dbscan_border_noise_component_partition_gate_pod_optix_numba`

Goal5095 adds a second bounded same-input fixture to the RT-DBSCAN paper app.
Unlike the first tiny fixture, this one explicitly contains:

- a non-core border point assigned to a cluster;
- two components;
- a distant noise point.

AuthorOfficial and RTDL's generic OptiX+Numba fixed-radius component-label route
now match exactly on both:

- the normalized component signature; and
- the canonical point partition, modulo component-label renaming.

```text
point_count=12
epsilon=0.35
min_points=5
core_count=10
component_count=2
component_sizes=[5,6]
noise_count=1
signature_matched=true
component_partition_matched=true
core_flags_matched=true
matched=true
```

## Fixture

```text
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/border_noise3d_component_signature.csv
```

Important ordering detail:

The border point is intentionally placed at index `0`. The author call-2 kernel
only processes hits under `xID > primID`, so placing the border point before its
core neighbor makes the same-input fixture exercise the author's border
assignment path instead of accidentally leaving the border point unassigned.

Expected CPU-reference behavior:

```text
component_labels=[0,0,0,0,0,0,1,1,1,1,1,-1]
core_flags=[0,1,1,1,1,1,1,1,1,1,1,0]
component_sizes=[5,6]
noise_count=1
```

## POD Evidence

POD:

```text
root@213.173.108.24 -p 13502
gpu=NVIDIA RTX 4000 Ada Generation
driver=550.127.05
```

Evidence:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/component_signature_border_noise_local_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_author_output_optix.jsonl
```

AuthorOfficial payload:

```text
component_labels=[0,0,0,0,0,0,1,1,1,1,1,-1]
component_sizes=[6,5]
core_count=10
core_flags=[0,1,1,1,1,1,1,1,1,1,1,0]
noise_count=1
parent_roots=[1,1,1,1,1,1,6,6,6,6,6,11]
```

Normalized AuthorOfficial signature:

```text
{core_count=10, component_sizes=[5,6], noise_count=1}
```

RTDL canonical partition:

```text
canonical_component_labels=[0,0,0,0,0,0,1,1,1,1,1,-1]
core_flags=[0,1,1,1,1,1,1,1,1,1,1,0]
```

RTDL signature derived from the partition:

```text
{core_count=10, component_sizes=[5,6], noise_count=1}
```

The gate no longer relies only on the sorted component-size signature. A border
point moved from one component to the other can preserve `[5,6]` after sorting;
the canonical point-partition comparison detects that case.

## RTDL Generic System Path

RTDL uses the same prepared OptiX+Numba grouped-stream system family as Goal5094,
but the amended gate uses the label-producing route so that it can compare
point partitions:

```text
prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns
```

Key metadata:

```text
partner_reference_contract=generic_prepared_optix_numba_grouped_stream_component_labels_3d
native_engine_row_contract=generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces
materializes_neighbor_rows=false
materializes_directed_adjacency_stream=false
rt_core_accelerated=true
partner=numba
```

This stronger comparator intentionally materializes the output component-label
column for the app-owned AuthorOfficial comparison. It does not add an
RT-DBSCAN-specific RTDL primitive.

No RT-DBSCAN-specific RTDL core primitive was added.

## Validation

Local tests:

```text
py -m unittest tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test
```

Observed:

```text
Ran 8 tests
OK
```

Full focused gate tests:

```text
py -m unittest \
  tests.goal5092_rt_dbscan_authorofficial_gate_packet_test \
  tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test
```

Observed:

```text
Ran 8 tests
OK
```

Additional regression added after external review:

```text
test_canonical_partition_detects_border_swap_that_signature_misses
```

This test proves the old signature-only comparator is blind to a border swap
that preserves the sorted component sizes, while the canonical partition
comparator rejects it.

## Claim Boundary

Authorized:

- second bounded same-input RT-DBSCAN component-partition gate passed;
- AuthorOfficial and RTDL match on canonical point partition, normalized
  signature, and core flags for the border/noise fixture;
- RTDL generic OptiX+Numba fixed-radius graph component-label path matches
  AuthorOfficial on the second fixture.

Not authorized:

- full RT-DBSCAN paper reproduction;
- exact paper dataset reproduction;
- exact author label ID parity;
- full DBSCAN output-format parity;
- performance or speedup.

## Next Work

RT-DBSCAN paper app now has two bounded AuthorOfficial gates: the earlier
core-count gate and the amended component-partition gate. The second fixture no
longer depends on signature-only equality for its border/noise claim.
The next substantive step should be one of:

1. add a larger representative same-input fixture;
2. add exact label-ID comparator only if the author ordering contract is
   explicitly accepted;
3. stop the RT-DBSCAN bounded line here and send Goals5093-5095 for review.
