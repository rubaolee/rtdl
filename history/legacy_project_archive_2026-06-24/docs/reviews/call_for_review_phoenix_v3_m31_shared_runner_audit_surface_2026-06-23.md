# Call For Review: Phoenix V3 M31 Shared Runner Audit Surface

Date: 2026-06-23
Status: `request_m31_external_review_not_release`

This review asks whether M31 is a correct Phoenix V3 trunk-first engineering
step. It does not ask for release authorization, all-app POD authorization, or
public speedup wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Patch Scope

Code:

- `src/rtdsl/prepared_execution.py`
- `scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py`
- `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py`
- `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py`
- `scripts/v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py`
- `scripts/v3_phoenix_rayjoin_point_location_runner_pod_ab.py`
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_rtnn_prepared_execution_runner_wiring_test.py`
- `tests/v3_phoenix_triangle_runner_m18_pod_ab_test.py`
- `tests/v3_phoenix_barnes_hut_runner_parity_pod_ab_test.py`
- `tests/v3_phoenix_step1_rtdbscan_trunk_probe_report_test.py`
- `tests/v3_phoenix_rayjoin_point_location_runner_pod_ab_test.py`
- `tests/v3_phoenix_hausdorff_threshold_runner_pod_ab_test.py`
- `tests/v3_phoenix_hausdorff_prepared_execution_runner_wiring_test.py`
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`

Reports:

- `docs/reports/phoenix_v3_post_m22_step_alignment_and_next_work_2026-06-23.md`
- `docs/reports/phoenix_v3_m31_shared_runner_step3_audit_surface_2026-06-23.md`
- `docs/reports/phoenix_v3_m31_prepared_session_family_audit_inventory_2026-06-23.md`
- `docs/reviews/external_review_blocked_phoenix_v3_m30_gemini_interim_review_2026-06-23.md`
- `docs/reviews/external_review_blocked_phoenix_v3_m31_gemini_interim_review_2026-06-23.md`

## Change Summary

M31 adds a shared audit surface for final `prepared_execution_session_runner`
metadata:

- `PREPARED_EXECUTION_SESSION_AUDIT_VERSION`
- `audit_prepared_execution_session_metadata(metadata)`
- `PreparedExecutionSessionResult.runtime_audit()`

The helper returns:

- whether productized runner was used;
- whether runtime executed;
- whether prepared-execution phase accounting exists and validates;
- whether `runtime_trunk_executes_end_to_end` is reported and true;
- whether `internal_device_residency_between_rtdl_phases` is reported and true;
- whether `hot_path_host_materialization` is reported and false;
- whether repeat timing and output-finalization timing are present;
- whether claim boundaries remain closed;
- whether the helper is marked as a Set-A probe candidate or Set-B control;
- whether `step3_residency_default_ready` is true;
- missing Step-3 fields when incomplete.

M31 also records `productized_execution_path: prepared_execution_session_runner`
in base runner metadata. It does **not** set
`runtime_trunk_executes_end_to_end=true` in the base runner; final wrappers must
still prove that field.

M31 wires the audit payload into future RTNN focused repeat50 evidence:

- summary field: `runner_step3_audit`;
- runner phase-row fields: `step3_residency_default_ready`,
  `step3_audit_status`, `step3_audit_missing_fields`;
- serious RTNN packet check: `runner_step3_residency_default_ready`.

M31 applies the same audit payload pattern to future Triangle focused evidence:

- runner variant fields: `step3_audit`, `step3_residency_default_ready`;
- summary fields: `runner_step3_audit`, `runner_step3_residency_default_ready`;
- non-dry-run fail-closed check:
  `runner_step3_residency_default_not_ready`.

M31 also applies the shared audit gate to the Barnes-Hut focused runner packet:

- runner row fields: `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, `step3_residency_default_ready`;
- summary fields: `runner_step3_audit_rows`,
  `runner_step3_residency_default_ready`;
- Step-1 candidate gate:
  `runner_step3_residency_default_ready_all_samples`.

M31 additionally wires the shared audit gate to the RTDBSCAN M3.4 repeated
runner packet:

- runner row fields: `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, `step3_residency_default_ready`;
- summary fields: `runner_step3_audit_rows`,
  `runner_step3_residency_default_ready_all_runner_samples`;
- no-release boundary preserved: M3.4 remains a legacy-parity/no-material-gain
  packet unless future POD evidence changes the measured result.

M31 also wires the shared audit gate to the RayJoin point-location focused
packet:

- runner row fields: `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, `step3_residency_default_ready`;
- summary fields: `runner_step3_audit_rows`,
  `runner_step3_residency_default_ready`;
- material status remains same-contract speedup gated plus audit-ready; audit
  readiness alone is not a speed claim.

M31 now wires the shared audit gate to the Hausdorff threshold focused packet:

- the app exposes per-directed-leg runner audit fields instead of only a
  combined summary;
- the packet script audits both directed legs with
  `audit_prepared_execution_session_metadata()`;
- the runner variant records `step3_audit`, `step3_audit_status`,
  `step3_audit_missing_fields`, and `step3_residency_default_ready`;
- no-release/no-all-app/no-broad-claim boundaries remain closed.

M31 also strengthens the core runner contract tests: RTNN ranked-summary,
RayJoin point-location, RTDBSCAN component-signature, Barnes-Hut aggregate-tree
fused vector-sum, Triangle weighted-summary, and segment-intersection topology
stream helper tests now assert
`runtime_audit()` reaches `accept_step3_ready`, instead of relying only on
route-script metadata checks.

The packet also records negative gates for runner-shaped helpers that lack real
Step-3 facts: base fixed-radius self-query is a blocked Set-A seed, while AABB
range rows, AABB counts, and OptiX AABB prepared-query-set counts are blocked
Set-B controls. These may report `runtime_executed=true`, but they must remain
`incomplete_step3_audit` until they report runtime-trunk execution, internal
residency, and no hot-path host materialization.

## Validation

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 34 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 42 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_m18_triangle_runner_harness_packet_test \
  tests.v3_phoenix_m16_triangle_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 54 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test
Ran 4 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_step1_rtdbscan_trunk_probe_report_test
Ran 3 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test
Ran 3 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
Ran 7 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test
Ran 4 tests
OK
```

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

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_phoenix_serious_v2x_paired_analysis_test
Ran 7 tests
OK
```

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

```text
py -3 -m py_compile src\rtdsl\prepared_execution.py tests\v3_phoenix_prepared_execution_session_runner_test.py
exit_code: 0
```

After wiring the RTNN, Triangle, Barnes-Hut, RTDBSCAN M3.4, and RayJoin
evidence scripts, full `py_compile` hit the known local Windows pycache
permission issue. A no-pyc syntax compile passed:

```text
syntax_compile_without_pyc_ok 5
```

```text
git diff --check
exit_code: 0
```

Windows Python emitted the known local warning:

```text
Could not find platform independent libraries <prefix>
```

## Reviewer Questions

1. Is M31 aligned with Claude's Step 3 requirement that phase accounting and
   residency become checkable first-class facts rather than prose?
2. Is it correct that base runner metadata may record
   `productized_execution_path=prepared_execution_session_runner`, while the
   base runner must **not** auto-claim `runtime_trunk_executes_end_to_end`?
3. Is the `step3_residency_default_ready` gate strict enough?
4. Does the helper avoid broad release/public/V3-over-V2/zero-copy claims?
5. Should the next engineering step use this helper to inventory route evidence
   and then promote continuation nodes into the runner core?
6. Does this patch authorize any all-app run, release, public speedup, broad
   V3-over-V2, true-zero-copy, automatic partner-selection, or V4 work?

## Requested Verdict Labels

Choose exactly one:

- `accept_m31_shared_audit_surface`
- `accept_with_amendments`
- `blocked_needs_code_changes`
- `reject_m31_wrong_direction`

Include blocking findings, required amendments if any, explicit answers to the
six questions, and an explicit non-authorization block.
