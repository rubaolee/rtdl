# Phoenix V3 Runner Fingerprint / Overhead Fix M3.2

Date: 2026-06-22
Status: `local_generic_runner_correctness_overhead_fix_not_pod_evidence`

## Summary

This patch implements the next action accepted by the RTDBSCAN M3.1
negative-classification 2-AI consensus:

```text
next_action: bounded_generic_runner_overhead_and_fingerprint_correctness_fix
```

It fixes the generic prepared execution runner's large-input fingerprint shape
and wires the RTDBSCAN component-signature runner route to precompute that
fingerprint outside the measured loop.

This is not pod performance evidence and does not authorize release or any
public speedup claim.

## What Changed

Code:

- `src/rtdsl/prepared_execution.py`
  - adds public `make_prepared_input_fingerprint`;
  - replaces truncated large sequence `repr(tuple(value))[:2048]` fingerprints
    with a full streaming SHA-256 digest over element reprs;
  - keeps bounded first/last repr samples for diagnostics only;
  - allows `run_radius_graph_component_signature_3d_prepared_session` to accept
    caller-supplied `point_rows_fingerprint`;
  - records `input_fingerprint_source` and
    `large_input_fingerprint_hot_path_avoided` metadata.
- `src/rtdsl/__init__.py`
  - exports `make_prepared_input_fingerprint`.
- `examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
  - precomputes `point_rows_for_runner` and
    `point_rows_fingerprint` once before the measured runner loop;
  - passes the precomputed fingerprint into
    `run_radius_graph_component_signature_3d_prepared_session`.

Tests:

- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
  - verifies long sequences that would share the old truncated prefix now have
    distinct SHA-256 fingerprints;
  - verifies caller-supplied fingerprints are recorded by the component
    signature helper.
- `tests/v3_phoenix_rtdbscan_component_signature_optimization_test.py`
  - verifies the real RTDBSCAN app branch precomputes and passes the
    fingerprint to the productized runner.

## Why This Was Needed

The M3.1 pod A/B showed:

```text
geomean_runner_vs_legacy_speedup: 0.5038091959795198
runner_metadata_present_all_runner_samples: true
signatures_stable: true
```

Claude and Codex agreed the classification was valid negative evidence. The
timing showed native grouped work was close to legacy, while Python-side runner
overhead dominated the loss. Claude also identified a correctness risk:
truncated sequence reprs are collision-prone cache-key material.

This patch addresses the generic issue directly. It does not add an
RTDBSCAN-specific native engine, shortcut, or app-specific route knob.

## Boundaries

```text
pod_performance_evidence: false
material_set_a_candidate: false
second_set_a_material_probe_obtained: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

## Verification

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_rtdbscan_component_signature_optimization_test
Ran 14 tests
OK

PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_rtdbscan_component_signature_optimization_test tests.v3_phoenix_next_dominant_hotpath_selection_test tests.v3_release_wording_gate_test
Ran 25 tests
OK
```

## Next Evidence Required

Run a focused same-hardware pod A/B that reuses the M3.1 comparison:

```text
legacy OptiX grouped-stream Numba column-signature
vs
runner-backed OptiX grouped-stream Numba column-signature after M3.2
```

This patch should count as progress only if the pod result shows:

```text
runner_metadata_present_all_runner_samples: true
signatures_stable: true
runner_vs_legacy_geomean >= 0.98x minimum
runner_vs_legacy_geomean >= 1.15x preferred for material Set-A candidacy
claim flags remain false
```

Until then, it is a local correctness/overhead fix, not V3 performance proof.

## Goal-Level Decision Audit

Decision: implement the bounded generic runner fingerprint/overhead fix before
another pod run.

1. Was I foolish?
   No for this decision.
2. What actions would have made this foolish?
   It would be foolish to leave a collision-prone cache-key path in place or
   to call this local fix a performance win before a pod A/B.
3. Was there another path?
   Yes. I could switch to another Set-A route, but the same runner fingerprint
   issue could affect other large-input routes.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is a focused pod A/B that tests whether the generic fix
   recovers the RTDBSCAN runner-backed route against the incumbent OptiX legacy
   path.
