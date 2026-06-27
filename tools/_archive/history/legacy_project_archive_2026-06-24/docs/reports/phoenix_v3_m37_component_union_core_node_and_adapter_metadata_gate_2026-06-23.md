# Phoenix V3 M37 Component-Union Core Node And Adapter Metadata Gate

Date: 2026-06-23

Status: `m37_component_union_core_node_local_ready_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
performance_claim_authorized: false
```

## Purpose

M37 implements the M35 work-queue item after M36: split component-union and
component-signature accounting so the union pass is visible as a generic V3
runtime node instead of being hidden inside an RTDBSCAN route packet.

This remains local contract work. It is not a benchmark result and not a
release claim; it is not a release packet.

## What Changed

Code:

- `src/rtdsl/prepared_execution.py`
  - added `run_radius_graph_component_union_3d_prepared_session`;
  - exported it through `prepared_execution.__all__`;
  - routes the fixed-radius component-union pass through
    `PreparedExecutionSessionTask`;
  - default replay path calls existing generic
    `radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns`;
  - records union-pass accounting separately from component-signature
    accounting;
  - fails closed if signature output is presented as union output;
  - after Claude review, tightened component-label accounting so
    `component_label_pass_accounted` requires both a label policy and a real
    `component_labels` output column.
- `src/rtdsl/__init__.py`
  - exports `run_radius_graph_component_union_3d_prepared_session`;
  - fixes the M36 surface drift by exporting
    `run_grouped_vector_sum_2d_prepared_session` at the top-level `rtdsl`
    package.

Tests and gates:

- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
  - verifies the component-union helper executes through the productized
    runner and reports Step-3/Step-4 metadata;
  - verifies signature output cannot satisfy the union helper's trunk-success
    predicate.
- `tests/v3_phoenix_m37_adapter_metadata_contract_test.py`
  - verifies the real grouped-vector adapter metadata path preserves
    `row_count` and `group_count`;
  - verifies component-union and component-signature use separate real adapter
    entrypoints.
- `scripts/v3_phoenix_prepared_session_surface_ledger_gate.py`
  - now checks the M37 ledger;
  - now checks both `prepared_execution.__all__` and top-level `rtdsl`
    exports.
- `docs/reports/phoenix_v3_m37_prepared_session_step4_surface_ledger_2026-06-23.md`
  - records the current 13-helper surface.

Current surface:

```text
public_helper_count: 13
ledger_row_count: 13
step4_ready: 9
blocked_set_a_seed: 1
blocked_set_b_control: 3
```

## Runtime Contract

`run_radius_graph_component_union_3d_prepared_session` is generic:

- primitive: `fixed_radius_graph_component_union_3d`;
- row contract: `generic_fixed_radius_graph_component_union_3d`;
- continuation contract:
  `generic_prepared_optix_numba_grouped_stream_component_labels_3d`;
- runtime trunk family:
  `fixed_radius_self_query_to_grouped_stream_component_union_3d`;
- productized execution path: `prepared_execution_session_runner`;
- explicit backend: `optix`;
- explicit partner: `numba`;
- app-specific native engine logic: false.

The helper surfaces:

- `component_union_phase_accounting_visible`;
- `component_union_policy`;
- `component_union_native_execution_path`;
- `component_union_native_elapsed_sec`;
- `component_union_pass_count`;
- grouped-union query block size/count;
- boundary-assignment policy/pass count;
- `component_label_pass_accounted`;
- `component_label_columns_present`;
- `component_signature_accounting_split`;
- `component_signature_pass_executed`.

The helper can be Step-4 ready only when component-union accounting is visible,
component-label output is accounted with a real `component_labels` output
column, component-signature work is not executed inside this node, internal
RTDL phase residency is reported, and no hot-path host materialization is
reported.

## Local Validation

Focused local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test \
  tests.v3_phoenix_m37_adapter_metadata_contract_test \
  tests.v3_release_wording_gate_test
Ran 50 tests in 5.134s
OK
```

Full local V3 rebuild matrix after M37:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 117
Ran 608 tests in 74.624s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stderr.txt
```

Claude external review accepted M37 with verdict
`accept_m37_component_union_core_node_continue`. Claude's non-blocking
component-label accounting suggestion was applied before final M37 closure and
the full matrix was rerun after that change.

## Read

M37 does not prove that component-union is now materially faster. It makes the
dominant union pass visible as a runner-callable core node and prevents
component-signature savings from hiding the union-pass cost.

The M36 carry-forward concern is addressed locally: the real
`prepare_grouped_vector_sum_2d_partner_columns_session` writes both
`row_count` and `group_count`, and the real
`run_grouped_vector_sum_2d_partner_columns_session` copies the prepared-session
metadata before adding replay facts. Focused grouped-reduction POD evidence
still requires a separate reviewed protocol.

All-app remains blocked until focused Set-A and Set-B preconditions are met and
externally reviewed.

## Goal-Level Decision Audit

Decision: implement a generic component-union prepared-session helper and a
metadata contract gate before any focused POD spend.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be rerunning RTDBSCAN or all-app while the union
   pass remained hidden inside a route packet and while M36's real-adapter
   metadata concern was only orally resolved.

3. Was there another path?

   Yes. Continue with route-specific RTDBSCAN signature tuning. That is
   rejected because M35 showed signature savings alone did not produce a
   material V3 win.

4. Can I now try a different path that actually solves the problem?

   Yes. The union pass is now a generic runner-callable node with separate
   accounting, fail-closed metadata, and current surface gates. The next path is
   external review, then only a focused same-contract probe if the local
   contract is accepted.

## Non-Authorization

This report authorizes no V3 release, no all-app POD spend, no public speedup
claims, no broad V3-over-V2.x claims, no true-zero-copy wording, no automatic
partner selection, no V4 work, no C ABI work, and no embedding work.
