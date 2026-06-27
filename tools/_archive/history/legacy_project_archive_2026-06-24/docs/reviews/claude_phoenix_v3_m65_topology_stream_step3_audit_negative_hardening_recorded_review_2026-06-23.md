# Recorded Review: Phoenix V3 M65 Topology-Stream Step3 Audit Negative Hardening

Reviewer: Claude Sonnet 4.6
Date: 2026-06-23
Verdict: `accept_m65_topology_stream_step3_negative_hardening_continue_local_no_pod_no_release`

---

## Files Reviewed

- `docs/reports/phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_2026-06-23.md`
- `docs/reports/phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md`
- `src/rtdsl/prepared_execution.py` (full, 3749 lines; focused on `audit_prepared_execution_session_metadata` at line 3355 and `audit_prepared_execution_continuation_metadata` at line 3486)
- `tests/v3_phoenix_prepared_execution_session_runner_test.py` (focused on negative sub-cases in `test_point_location_topology_stream_helper_routes_generic_family_through_runner` and the new `test_non_topology_stream_set_a_bypasses_topology_bridge_gate`)
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py` (focused on negative sub-cases in `test_generic_runner_metadata_with_fake_segment_stream`)

---

## Answers to Review Questions

### Q1. Do the new negative tests cover the M64 carry-forward debt?

Yes, completely. The M64 review recorded a low-priority suggestion to exercise additional negative bridge failure paths. M65 implements all five:

1. Partial M3 phase table (`topology_stream_m3_phase_table_complete=False` with non-empty `topology_stream_m3_missing_phases_for_public_row`)
2. Bad bridge contract (contract string set to an arbitrary non-conforming value)
3. Bad bridge status (status set to `"partial_non_authorizing_m3_bridge"`)
4. Public-row authorization flag set True (`topology_stream_m3_bridge_public_row_authorized=True`)
5. M7 authorization flag set True (`topology_stream_m3_bridge_m7_promotion_authorized=True`)

Each is exercised as a `subTest` variant within the positive-path test, mutating only the field under test and asserting the audit outcome.

### Q2. Do they prove bad bridge contract, bad bridge status, partial M3 table, and authorization-flag mistakes fail Step3?

Yes. Every negative sub-case asserts all three of:

- `broken_audit["status"] == "incomplete_step3_audit"`
- `broken_audit["topology_stream_m3_bridge_ready"] is False`
- `"complete_non_authorizing_topology_stream_m3_bridge" in broken_audit["missing_step3_fields"]`

Each sub-case also checks the specific disaggregated sub-field expected to change:

| Sub-case | Expected changed sub-field |
|---|---|
| `partial_phase_table` | `topology_stream_m3_bridge_complete=False` |
| `bad_bridge_contract` | `topology_stream_m3_bridge_contract_ok=False` |
| `bad_bridge_status` | `topology_stream_m3_bridge_complete=False` |
| `bridge_public_row_authorized` | `topology_stream_m3_bridge_non_authorizing=False` |
| `bridge_m7_authorized` | `topology_stream_m3_bridge_non_authorizing=False` |

The implementation in `audit_prepared_execution_session_metadata` (lines 3390-3435) is verified to match these assertions:

- Contract check uses exact string equality against `"prepared_execution_to_topology_stream_m3_bridge_v1"`.
- Completeness check requires all three of: status string, phase table complete flag, and empty missing-phases tuple.
- Non-authorizing check uses `is False` comparisons on both auth flags, so a missing key (returning `None`) also causes `non_authorizing=False` -- the safe/blocking direction.

### Q3. Does segment-intersection now have its own broken-bridge negative path?

Yes. `test_generic_runner_metadata_with_fake_segment_stream` in `v3_phoenix_spatial_segment_intersection_runner_wiring_test.py` contains an identical `negative_cases` block with the same five variants. Each applies the same mutation, runs `audit_prepared_execution_session_metadata` on the broken metadata, and asserts `status=="incomplete_step3_audit"`, `topology_stream_m3_bridge_ready is False`, and the missing-field sentinel present.

Point-location and segment-intersection now have structural parity at this gate.

### Q4. Are non-authorization boundaries preserved?

Yes. `test_non_topology_stream_set_a_bypasses_topology_bridge_gate` (added in M65) constructs synthetic metadata with `primitive_family="fixed_radius_ranked_summary_3d"` and `set_a_probe_candidate=True` -- a legitimate Set-A family that is not topology-stream. The audit returns `accept_step3_ready`, confirms `topology_stream_set_a_candidate is False`, `topology_stream_m3_bridge_ready is True`, and asserts the bridge sentinel is absent from `missing_step3_fields`.

The implementation guards this correctly: `topology_stream_m3_bridge_ready = not topology_stream_set_a_candidate or (...)`. The short-circuit fires for any non-topology-stream primitive family regardless of bridge metadata presence, so the gate cannot over-constrain families it was not designed to regulate.

Additionally, `test_fixed_radius_ranked_summary_helper_routes_generic_family_through_runner` runs the full ranked-summary helper end-to-end and also reaches `accept_step3_ready`, providing independent confirmation via a real session result rather than synthetic metadata.

### Q5. May local Phoenix V3 runtime work continue after M65?

Yes. M65 introduces no new runtime surface, no new public API, and no changes to session execution paths. It is purely test hardening. The test count increases from 43 to 44, consistent with adding one new top-level test method (`test_non_topology_stream_set_a_bypasses_topology_bridge_gate`); the new negative sub-cases are `subTest` variants within existing test methods and do not inflate the top-level count. All 44 tests pass.

The audit gate is machine-verified to be complete and correctly scoped. Local runtime work may continue.

### Q6. What smallest fixes, if any, are required before M66?

None. There are no blocking issues.

---

## Non-Authorization Statement

This review does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- focused POD spend
- public speedup wording
- broad V3-over-V2 claim
- whole-app speedup claim
- paper reproduction claim
- RTDL-beats-RayJoin claim
- true-zero-copy claim
- future-version host integration work
- external device-buffer interop claim
- low-level host interface work
- watch-row closure

---

## Carry-Forward P2 Suggestions

These are observations, not blockers. They do not gate M66.

**P2-A: Missing-key behavior of auth-flag check is implicit.**
The non-authorizing check uses `payload.get("topology_stream_m3_bridge_public_row_authorized") is False`. If those keys are absent entirely from a metadata dict, `get()` returns `None` and `None is False` evaluates to `False`, making `non_authorizing=False` and therefore the bridge not ready. This is the conservative/blocking direction and the correct behavior. However, no test exercises this path explicitly (keys absent vs. keys set True). A future test verifying the absent-key case would make the invariant explicit.

**P2-B: Set-B families not explicitly tested for bridge bypass.**
The bypass test uses a Set-A non-topology-stream family. Set-B control candidates (`set_b_control_candidate=True`, `set_a_probe_candidate=False`) are not checked by any test to confirm they also bypass the topology-stream bridge gate. The implementation is correct (bridge gate is conditional only on `topology_stream_set_a_candidate`, which requires `set_a_probe_candidate and "topology_stream" in primitive_family`), but a confirming test would be straightforward to add.

Neither P2 suggestion requires action before M66.
