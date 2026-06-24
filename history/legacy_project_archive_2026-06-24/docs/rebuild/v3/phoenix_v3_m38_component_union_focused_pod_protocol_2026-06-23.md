# Phoenix V3 M38 Component-Union Focused POD Protocol

Status: `m38_protocol_ready_for_review_no_pod_run`

This protocol does not authorize a POD run. It does not authorize V3 release,
all-app POD spend, public speedup wording, broad V3-over-V2.x wording,
true-zero-copy wording, V4 work, C ABI work, or embedding work.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
component_union_material_probe_closed: false
```

## Bottom Line

M38 freezes the focused same-contract protocol for the M37 component-union core
node. It does not run POD.

The protocol exists because M37 made the component-union pass visible as a
generic runner-callable V3 node, but that is still structural evidence only.
The next evidence must measure the productized runner path against same-contract
controls without substituting component-signature output for component-union
labels.

## Exact Row

```text
row: component_union_clustered3d_262144_points_repeat5_m38_focused_probe
workload: clustered 3D fixed-radius component-union labels
point_count: 262144
radius: 3.0
min_neighbors: 4
warmup: 1
repeat: 5
serious_scale_floor_points: 262144
smoke_rows_do_not_count: true
```

This is generic fixed-radius component-union label work. It is not full DBSCAN
paper reproduction and not a broad RTDBSCAN app speedup claim.

## Variants

M38 requires three variants on the same generated point set:

```text
embree_same_contract_component_union_control
legacy_optix_grouped_stream_component_labels
productized_prepared_execution_runner
```

All three commands are proposed M39 harness commands only. M38 does not claim
that `scripts/v3_phoenix_component_union_m38_pod_ab.py` already exists, and it
does not authorize running it on POD.

The runner route must use:

```text
run_radius_graph_component_union_3d_prepared_session
```

and must emit:

```text
runtime_executed=true
runtime_trunk_executes_end_to_end=true
productized_execution_path=prepared_execution_session_runner
primitive_family=fixed_radius_graph_component_union
continuation_contract=generic_prepared_optix_numba_grouped_stream_component_labels_3d
component_union_phase_accounting_visible=true
component_label_columns_present=true
component_signature_pass_executed=false
internal_device_residency_between_rtdl_phases=true
hot_path_host_materialization=false
```

Component signatures may be used only as correctness digests after component
labels exist. A signature-only route cannot replace component-union label work.

## Success Bars

- Correctness: all variants must produce matching canonical component
  signatures from component-label outputs.
- Productized runtime: the runner metadata must prove the M37 path executed
  end to end.
- Material Set-A candidate: runner OptiX must beat Embree same-contract control
  by at least `1.20x` on both hot query median and runner-inclusive wall.
- Legacy no-regression: runner-inclusive wall must be at least `0.98x` of the
  legacy OptiX grouped-stream component-label route.
- Claim boundary: release, public speedup, broad V3-over-V2, V4, embedding,
  and zero-copy flags stay false.

## Failure Actions

- No runner harness: stop and create/review a local M39 harness; do not spend
  POD.
- Hardware gate failure: stop and record environment failure.
- Correctness mismatch: stop; no performance interpretation.
- Component signature substituted for labels: invalid run.
- Missing M37 metadata: productized-runner failure, no Set-A credit.
- Runner below `1.20x` over Embree: coverage or negative evidence only.
- Runner below `0.98x` versus legacy OptiX wall: productized coverage only
  unless a later 2-AI review accepts a specific exception.

## Resource Budget If Later Authorized

```text
M39 runner harness local work: 1.5-3.0 h
focused POD wall time: 0.75-1.5 h
focused POD cost at $1 / 4 h: $0.19-$0.38
hard cap before new review: 2 h / $0.50
all-app POD: not authorized
```

The focused run must print heartbeat output at least every 30 seconds.

## Review Request

M38 asks external review to choose one:

```text
accept_m38_authorize_m39_runner_harness_no_pod
accept_m38_authorize_one_focused_component_union_pod_after_harness_gate
revise_m38_protocol
reject_m38_protocol
```

Recommended conservative verdict:
`accept_m38_authorize_m39_runner_harness_no_pod`, because no reviewed focused
M37 component-union runner harness exists yet.

## Goal-Level Decision Audit

Decision: write a focused component-union protocol instead of running POD
immediately after M37.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to spend POD before freezing labels-vs-signature
   semantics, controls, metrics, resource cap, and fail-closed interpretation.

3. Was there another path?

   Yes. Run a focused POD immediately because the core node exists. That risks
   measuring an unreviewed harness or component-signature shortcut.

4. Can I now try a different path?

   Yes. Freeze the row, variants, metadata gates, success bars, failure
   classifications, and cost cap; then seek 2-AI review before spending POD.
