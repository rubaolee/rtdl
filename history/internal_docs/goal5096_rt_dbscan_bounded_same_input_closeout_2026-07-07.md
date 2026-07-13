# Goal5096 RT-DBSCAN Bounded Same-Input Closeout

Date: 2026-07-07

## Verdict

```text
completed_rt_dbscan_bounded_same_input_core_count_and_component_partition_line
```

This closes the current RT-DBSCAN bounded same-input line at the level of:

- AuthorOfficial core-count equality on a tiny 3D fixture; and
- AuthorOfficial component-partition equality on tiny and border/noise 3D
  fixtures.

It does not close full RT-DBSCAN paper reproduction.

## Closed Evidence

### Goal5093: core-count gate

Evidence:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_optix_summary.json
```

Result:

```text
point_count=8
epsilon=0.35
min_points=3
author.core_count=7
rtdl.core_count=7
matched=true
bounded_core_count_reproduction_claim_authorized=true
paper_reproduction_claim_authorized=false
performance_claim_authorized=false
```

RTDL route:

```text
fixed_radius_count_threshold_3d / prepared OptiX count-threshold device columns
```

### Goal5094/5095: component-partition gates

The original Goal5094 signature-only gate was useful but too weak for border
assignment claims. Goal5095, after strict review, amended the gate to compare
canonical point partitions modulo component-label renaming.

Evidence:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_gate_pod_optix_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_component_signature_border_noise_pod_optix_summary.json
```

All three summaries now use:

```text
schema=rtdl.paper_reproduction.rt_dbscan.authorofficial_component_partition_gate.v2
signature_matched=true
component_partition_matched=true
core_flags_matched=true
matched=true
```

Tiny fixture:

```text
canonical_component_labels=[0,0,0,0,1,1,1,-1]
core_flags=[1,1,1,1,1,1,1,0]
signature={core_count=7, component_sizes=[3,4], noise_count=1}
```

Border/noise fixture:

```text
canonical_component_labels=[0,0,0,0,0,0,1,1,1,1,1,-1]
core_flags=[0,1,1,1,1,1,1,1,1,1,1,0]
signature={core_count=10, component_sizes=[5,6], noise_count=1}
```

RTDL route:

```text
prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns
```

The RTDL route is generic fixed-radius graph component-label infrastructure, not
an RT-DBSCAN-specific core primitive.

## External Review State

Goal5095 amendment was externally reviewed and approved:

```text
history/internal_docs/review_goal5095_amended_component_partition_gate_verified_2026-07-07.md
verdict=approve_goal5095_amended_component_partition_gate
```

The review specifically verifies that the prior signature-only blind spot is
closed by canonical point-partition equality.

Goals5093-5095 as a combined bounded line still need consolidated review if the
project wants a single external sign-off over the whole packet.

## Claim Boundary

Authorized:

- bounded same-input core-count equality against patched AuthorOfficial;
- bounded same-input canonical component-partition equality against patched
  AuthorOfficial on tiny and border/noise fixtures;
- use of generic RTDL fixed-radius count-threshold and component-label routes in
  a paper-app comparator.

Not authorized:

- full RT-DBSCAN paper reproduction;
- exact paper dataset reproduction;
- exact author label-ID parity;
- full DBSCAN output-format parity;
- author performance parity;
- whole-program DBSCAN speedup;
- claim that RTDL has a DBSCAN-specific core primitive;
- arbitrary clustering acceleration claims.

## Tests And Validation

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

The test suite includes:

```text
test_canonical_partition_detects_border_swap_that_signature_misses
```

This verifies that the new comparator detects the exact failure mode that the
old sorted component-size signature would have missed.

## Next Options

Stop here if the project only needs a third paper-app bounded correctness line.

Continue only with an explicit new goal:

1. larger representative same-input fixture with canonical partition equality;
2. exact paper dataset provenance;
3. independent full RT-DBSCAN pipeline reproduction;
4. performance comparison under pinned input/regime.

Each option is a separate line and must not inherit the bounded-line closeout as
full paper reproduction.
