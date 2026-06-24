# Phoenix V3 M31 Shared Runner Step-3 Audit Surface

Date: 2026-06-23

Status: `shared_runner_audit_surface_added_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
performance_claim_authorized: false
```

## Change

M31 adds a shared audit surface for `prepared_execution_session_runner` metadata:

- `audit_prepared_execution_session_metadata(metadata)`
- `PreparedExecutionSessionResult.runtime_audit()`
- `PREPARED_EXECUTION_SESSION_AUDIT_VERSION`

This does not change benchmark route logic or measured performance. It turns
Step 3 into a checkable contract: a route is only `step3_residency_default_ready`
when the final metadata reports all of the following:

- productized runner used;
- runtime executed;
- prepared-execution phase accounting exists and validates;
- `runtime_trunk_executes_end_to_end` is reported and true;
- `internal_device_residency_between_rtdl_phases` is reported and true;
- `hot_path_host_materialization` is reported and false;
- measured repeat timing and output-finalization timing are present;
- Set-A probe / Set-B control classification is echoed for review;
- release/public/broad/zero-copy/automatic-partner claim boundaries remain closed.

M31 also wires the audit payload into future RTNN focused repeat50 evidence
generation:

- `scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py`
  now records `runner_step3_audit` in the summary payload;
- the runner phase row records `step3_residency_default_ready`,
  `step3_audit_status`, and `step3_audit_missing_fields`;
- the serious RTNN packet check now requires Step-3 audit readiness unless the
  run is explicitly marked local smoke.

M31 applies the same audit payload pattern to future Triangle focused evidence:

- `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py` now records `step3_audit`
  and `step3_residency_default_ready` on the runner variant;
- the summary records `runner_step3_audit` and
  `runner_step3_residency_default_ready`;
- non-dry-run Triangle failure checks now fail closed if the runner is not
  Step-3 residency-default ready.

M31 also applies the shared audit gate to the Barnes-Hut focused runner packet:

- `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py` now calls
  `audit_prepared_execution_session_metadata()` for the runner metadata;
- each runner row records `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, and `step3_residency_default_ready`;
- the summary records `runner_step3_audit_rows` and
  `runner_step3_residency_default_ready`;
- the Step-1 replacement candidate gate now requires
  `runner_step3_residency_default_ready_all_samples`.

M31 additionally wires the shared audit gate to the RTDBSCAN M3.4 repeated
runner packet:

- `scripts/v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py` now calls
  `audit_prepared_execution_session_metadata()` for the final runner metadata;
- each runner row records `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, and `step3_residency_default_ready`;
- the summary records `runner_step3_audit_rows` and
  `runner_step3_residency_default_ready_all_runner_samples`;
- the existing negative/no-release interpretation remains unchanged: M3.4 is
  still legacy-parity recovery, not a material Set-A speedup.

M31 also wires the shared audit gate to the RayJoin point-location focused
packet:

- `scripts/v3_phoenix_rayjoin_point_location_runner_pod_ab.py` now calls
  `audit_prepared_execution_session_metadata()` for the runner metadata;
- each runner row records `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, and `step3_residency_default_ready`;
- the summary records `runner_step3_audit_rows` and
  `runner_step3_residency_default_ready`;
- material status still requires same-contract legacy-over-runner speedup plus
  Step-3 audit readiness; audit readiness alone is not a performance claim.

M31 now also wires the shared audit gate to the Hausdorff threshold runner
packet:

- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
  exposes the per-directed-leg runner audit fields instead of only a combined
  summary;
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py` audits both
  directed legs with `audit_prepared_execution_session_metadata()`;
- the runner variant records `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, and `step3_residency_default_ready`;
- material/release status remains unchanged: this is focused evidence plumbing,
  not broad Hausdorff, all-app, or V3-over-V2 authorization.

M31 also strengthens the core runner contract tests: RTNN ranked-summary,
RayJoin point-location, RTDBSCAN component-signature, Barnes-Hut aggregate-tree
fused vector-sum, Triangle weighted-summary, and segment-intersection topology
stream helper tests now assert
`runtime_audit()` reaches `accept_step3_ready`, rather than relying only on
route-script metadata checks.

## Why This Matters

Claude's trunk-first critique was not just "make a runner exist." It required
residency and phase accounting to become first-class facts, not prose. Before
M31, wrappers could expose those fields, but there was no shared check that
distinguished:

- a base runner that executed but has not proven residency; from
- a focused Set-A route whose final metadata proves phase accounting,
  end-to-end trunk execution, internal residency, and no hot-path host
  materialization.

M31 makes that distinction explicit.

## Goal-Level Decision Audit

Decision: while Claude is temporarily unavailable, continue local M31 work by
wiring the shared Step-3 audit gate into the remaining focused evidence packets,
without running all-app or making release/performance claims.

1. Was I foolish? No.
2. If yes, what actions made it foolish? The foolish action would have been to
   wait idle for Claude or to run broad benchmarks before the shared audit gate
   exists. This change did neither.
3. Was there another path? Yes: wait for Claude, or chase another benchmark
   number. Waiting would waste local work time; chasing numbers before audit
   gates would repeat the old leaf-first mistake.
4. Can I now try a different path that solves the problem? Yes: keep making the
   runtime evidence path shared, strict, and reviewable first; only after
   external review and focused gates pass should POD measurement expand.

## Validation

Focused runner test:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 34 tests
OK
```

RTNN audit/evidence wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 42 tests
OK
```

Triangle audit/evidence wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_m18_triangle_runner_harness_packet_test \
  tests.v3_phoenix_m16_triangle_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 54 tests
OK
```

Barnes-Hut focused packet audit wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test
Ran 4 tests
OK
```

RTDBSCAN M3.4 repeated-runner packet audit wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_step1_rtdbscan_trunk_probe_report_test
Ran 3 tests
OK
```

RayJoin point-location packet audit wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test
Ran 3 tests
OK
```

Hausdorff threshold runner packet audit wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
Ran 7 tests
OK
```

Segment-intersection topology-stream helper audit wiring:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test
Ran 4 tests
OK
```

Related V3 wrapper/evidence tests:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test \
  tests.v3_phoenix_step2_rayjoin_runner_report_test
Ran 30 tests
OK
```

Release wording and scorecard gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_phoenix_serious_v2x_paired_analysis_test
Ran 7 tests
OK
```

Combined M31 audit/evidence/release gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_m18_triangle_runner_harness_packet_test \
  tests.v3_phoenix_m16_triangle_runner_wiring_test \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test \
  tests.v3_phoenix_step1_rtdbscan_trunk_probe_report_test \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test
Ran 88 tests
OK
```

After wiring the RTNN, Triangle, Barnes-Hut, RTDBSCAN M3.4, RayJoin, and
Hausdorff evidence scripts, full `py_compile` hit the known local Windows
pycache permission issue. The affected files were still imported and exercised
by the 84-test focused gate above. Earlier no-pyc syntax compile also passed:

```text
syntax_compile_without_pyc_ok 5
```

Windows Python emitted the known local warning:

```text
Could not find platform independent libraries <prefix>
```

The warning did not prevent tests from passing.

## Boundaries

M31 does not authorize:

- V3 release;
- public speedup wording;
- broad V3-over-V2 wording;
- all-app POD spend;
- true zero-copy wording;
- V4 / C ABI / embedding / external-buffer wording;
- a claim that all Set-A routes are now residency-ready.

## Next Work

1. Retry Claude M30 RTNN review when Claude is ready.
2. Use the M31 audit helper to inventory all current prepared-session families.
3. Promote the most reusable continuation families into runner-callable nodes
   where they still remain app-mode route code.

## Goal-Level Decision Audit

Decision: add a shared audit helper instead of manually declaring Step 3 done.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be to set `runtime_trunk_executes_end_to_end=true`
   in the base runner for every route. M31 avoids that and requires final
   metadata proof.

3. Was there another path?

   Yes: continue writing route-specific prose or tune another app row. That
   would not make residency/phase accounting a reusable V3 engine contract.

4. Can I now try a different path that actually solves the problem?

   Yes. The audit helper lets the project inventory and enforce Step 3 across
   all families before another all-app run.
