# Goal5095 Review Amendment Response

Date: 2026-07-07

## Context

External review of Goal5095 returned:

```text
verdict: revise_goal5095_rt_dbscan_border_noise_gate
```

The blocking finding was correct. The original POD comparator only compared the
normalized component signature:

```text
{core_count, sorted(component_sizes), noise_count}
```

That signature is blind to a border point moving from one component to another
when the sorted component-size multiset remains unchanged. Therefore the old
wording "covers border assignment" was an overclaim.

## Amendments Implemented

### RA-1: remove the border-assignment overclaim

The Goal5095 report, call-for-review, results README, and manifest now describe
the gate as a bounded component-partition gate. They no longer claim that a
signature-only comparison validates border assignment.

### RA-2: add partition-equivalence comparison

`run_authorofficial_component_signature_gate.py` now uses the label-producing
generic RTDL route:

```text
prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns
```

The app-owned comparator now computes:

```text
canonical_component_labels
signature_matched
component_partition_matched
core_flags_matched
matched = signature_matched && component_partition_matched && core_flags_matched
```

Canonical partition comparison remaps nonnegative component IDs in point order
and preserves `-1` for noise. This avoids exact author label-ID dependence while
still detecting a border point assigned to the wrong component.

The signature summary is still recorded, but it is no longer the sole gate.

## POD Evidence

POD:

```text
root@213.173.108.24 -p 13502
gpu=NVIDIA RTX 4000 Ada Generation
driver=550.127.05
```

Tiny fixture:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_optix_summary.json
schema=rtdl.paper_reproduction.rt_dbscan.authorofficial_component_partition_gate.v2
matched=true
signature_matched=true
component_partition_matched=true
core_flags_matched=true
canonical_component_labels=[0,0,0,0,1,1,1,-1]
```

Border/noise fixture:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
schema=rtdl.paper_reproduction.rt_dbscan.authorofficial_component_partition_gate.v2
matched=true
signature_matched=true
component_partition_matched=true
core_flags_matched=true
canonical_component_labels=[0,0,0,0,0,0,1,1,1,1,1,-1]
core_flags=[0,1,1,1,1,1,1,1,1,1,1,0]
```

## Regression Tests

Focused local tests:

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

New regression:

```text
test_canonical_partition_detects_border_swap_that_signature_misses
```

This test constructs the exact failure mode identified by review: a border swap
that preserves the sorted component-size signature but changes the canonical
point partition.

## Claim Boundary

Authorized after amendment:

- bounded same-input AuthorOfficial-vs-RTDL component partition equality on the
  tiny fixture and border/noise fixture;
- normalized component signature equality as a derived summary;
- RTDL generic OptiX+Numba component-label route exercised by the paper app.

Not authorized:

- exact author label-ID parity;
- full DBSCAN output-format parity;
- exact paper dataset reproduction;
- full RT-DBSCAN paper reproduction;
- performance or speedup.

## Review Request

Please re-review Goal5095 with the amendment in place. The prior blocking
finding should be checked against:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
tests/goal5094_rt_dbscan_authorofficial_component_signature_gate_test.py
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
history/internal_docs/goal5095_rt_dbscan_border_noise_component_signature_gate_2026-07-07.md
```

Requested verdict:

```text
approve_goal5095_amended_component_partition_gate
```
