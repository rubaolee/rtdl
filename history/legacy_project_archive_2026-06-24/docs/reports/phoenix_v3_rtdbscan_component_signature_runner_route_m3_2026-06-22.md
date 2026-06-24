# Phoenix V3 RTDBSCAN Component-Signature Runner Route M3

Date: 2026-06-22
Status: local generic-runner contract passed; not release evidence.

## Summary

This records the first M3 step toward Claude/Codex's accepted next priority:
RTDBSCAN / grouped-reduction / component-union continuation through the
productized prepared execution/session runner.

The new runtime surface is app-agnostic:

```text
function: run_radius_graph_component_signature_3d_prepared_session
workflow_name: radius_graph_component_signature_3d_prepared_session
primitive: fixed_radius_graph_component_signature_3d
primitive_family: fixed_radius_graph_component_signature
continuation_contract: grouped_stream_component_size_signature_3d
row_contract: generic_fixed_radius_graph_component_signature_3d
productized_execution_path: prepared_execution_session_runner
```

The function is in `src/rtdsl/prepared_execution.py` and is exported from
`src/rtdsl/__init__.py`.

## What It Does

The wrapper routes a prepared fixed-radius graph component-signature
continuation through `run_prepared_execution_session`. The caller still chooses
the partner, cache, warmup count, validation, and optional injected
prepare/run functions.

Default production binding:

```text
prepare: prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
run: radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns
partner: explicit; default production path currently expects numba
```

Contract-test binding:

```text
prepare_session: fake prepared component-signature object
run_component_signature: injected fake component-signature runner
```

## Boundaries

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_allowed: false
full_all_app_rerun_authorized_by_this_packet: false
```

This is not a DBSCAN-native ABI, not full RTDBSCAN, not paper reproduction, and
not a pod performance result. It is a generic runner contract step toward the
second Set-A proof required by the current Claude/Codex consensus.

## Verification

Focused test:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 10 tests
OK
```

The new test verifies:

- `runtime_executed: true`;
- cache miss on first call and cache hit on the second call;
- explicit `partner: numba`;
- primitive name remains `fixed_radius_graph_component_signature_3d`, not an
  RTDBSCAN or DBSCAN-shaped name;
- point-id and core-flag materialization flags remain false in the injected
  continuation metadata;
- release/public/broad/true-zero-copy/automatic-selection flags remain false.

## Next Work

1. Wire this generic wrapper into the existing RTDBSCAN component-signature
   benchmark route without adding RTDBSCAN-specific native engine logic.
2. Run a focused same-hardware pod A/B for the runner-backed route.
3. Accept it as the second Set-A focused probe only if the measured win comes
   from `productized_execution_path: prepared_execution_session_runner` and
   clears the current focused lower bound from review (`>= 1.15x` wall, with
   `1.20x` preferred).
4. Do not run all-app until at least two Set-A probes have runner-backed focused
   evidence.

## Goal-Level Decision Audit

Decision: add an app-agnostic component-signature runner wrapper before
touching the RTDBSCAN benchmark route.

1. Was I foolish?
   No for this decision. It follows the accepted redirect and avoids a
   DBSCAN-shaped primitive name.
2. What actions would have made this foolish?
   It would be foolish to add a native RTDBSCAN ABI, route only a benchmark-app
   shortcut, or call this local contract a performance result.
3. Was there another path?
   Yes. I could have patched the benchmark app directly, but that would risk
   app-specific drift before the shared runtime surface existed.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is to bind this generic runner into the benchmark route
   and then use the pod only for focused Set-A evidence, not for another
   premature all-app run.

